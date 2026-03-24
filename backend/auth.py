"""Authentication and MFA management for TennisPro."""
import bcrypt
import pyotp
import qrcode
import string
import os
import smtplib
import secrets
import hashlib
import hmac
import importlib
from io import BytesIO
from email.message import EmailMessage
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import User, SessionLocal
from backend.utils import (
    validate_email,
    validate_password,
    validate_username,
    normalize_input,
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # Optional in production environments that provide env vars directly.
    pass

try:
    _fernet_mod = importlib.import_module("cryptography.fernet")
    Fernet = _fernet_mod.Fernet
    InvalidToken = _fernet_mod.InvalidToken
except Exception:
    Fernet = None
    InvalidToken = Exception


class AuthManager:
    """Manages user authentication and MFA."""

    # In-memory rate limit buckets: {bucket_key: [attempt_count, first_attempt_time]}
    _RATE_LIMITS = {}

    @staticmethod
    def _get_config_value(key: str, default: str = "") -> str:
        """Read config from env first, then Streamlit secrets."""
        env_value = os.getenv(key)
        if env_value is not None:
            env_value = str(env_value).strip()
            if env_value:
                return env_value

        try:
            import streamlit as st
            secret_value = st.secrets.get(key)
            if secret_value is not None:
                secret_value = str(secret_value).strip()
                if secret_value:
                    return secret_value
        except Exception:
            pass

        return default

    @staticmethod
    def _get_config_source(key: str) -> str:
        """Return where a config value is loaded from."""
        env_value = os.getenv(key)
        if env_value is not None and str(env_value).strip():
            return "environment"

        try:
            import streamlit as st
            secret_value = st.secrets.get(key)
            if secret_value is not None and str(secret_value).strip():
                return "streamlit_secrets"
        except Exception:
            pass

        return "missing"

    @staticmethod
    def _is_email_configured() -> bool:
        """Check whether SMTP settings are available."""
        return all([
            AuthManager._get_config_value("SMTP_HOST"),
            AuthManager._get_config_value("SMTP_PORT"),
            AuthManager._get_config_value("SMTP_USERNAME"),
            AuthManager._get_config_value("SMTP_PASSWORD")
        ])

    @staticmethod
    def get_email_configuration_status() -> dict:
        """Return SMTP configuration status for diagnostics in UI."""
        required_keys = ["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD"]
        sources = {key: AuthManager._get_config_source(key) for key in required_keys}
        missing = [key for key in required_keys if sources[key] == "missing"]
        smtp_host = AuthManager._get_config_value("SMTP_HOST", "")

        provider_hint = ""
        if "gmail" in smtp_host.lower():
            provider_hint = (
                "Gmail requires a 16-character App Password when 2-Step Verification is enabled. "
                "Regular account passwords will fail with 535 BadCredentials."
            )

        return {
            "configured": len(missing) == 0,
            "missing_keys": missing,
            "sources": sources,
            "smtp_from_email_set": bool(AuthManager._get_config_value("SMTP_FROM_EMAIL")),
            "smtp_use_tls": AuthManager._get_config_value("SMTP_USE_TLS", "true").lower() == "true",
            "provider_hint": provider_hint,
        }

    @staticmethod
    def _verification_code_pepper() -> str:
        """Get pepper used for verification code hashing."""
        return AuthManager._get_config_value("VERIFICATION_CODE_PEPPER", "dev-only-change-me")

    @staticmethod
    def _hash_verification_code(code: str) -> str:
        """Hash verification code before storage."""
        payload = f"{code}:{AuthManager._verification_code_pepper()}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _check_rate_limit(bucket: str, limit: int, window_seconds: int) -> bool:
        """Return True if action is allowed under configured rate limits."""
        now = datetime.utcnow()
        current = AuthManager._RATE_LIMITS.get(bucket)

        if not current:
            AuthManager._RATE_LIMITS[bucket] = [1, now]
            return True

        count, start = current
        if (now - start).total_seconds() > window_seconds:
            AuthManager._RATE_LIMITS[bucket] = [1, now]
            return True

        if count >= limit:
            return False

        AuthManager._RATE_LIMITS[bucket][0] += 1
        return True

    @staticmethod
    def _clear_rate_limit(bucket: str) -> None:
        """Clear a rate limit bucket after successful authentication."""
        AuthManager._RATE_LIMITS.pop(bucket, None)

    @staticmethod
    def _get_cipher():
        """Build encryption cipher if APP_ENCRYPTION_KEY is provided."""
        if Fernet is None:
            return None

        key = AuthManager._get_config_value("APP_ENCRYPTION_KEY")
        if not key:
            return None

        try:
            return Fernet(key.encode("utf-8"))
        except Exception:
            return None

    @staticmethod
    def _encrypt_sensitive(value: str) -> str:
        """Encrypt sensitive values when cipher key is configured."""
        cipher = AuthManager._get_cipher()
        if not cipher or not value:
            return value

        token = cipher.encrypt(value.encode("utf-8")).decode("utf-8")
        return f"enc:{token}"

    @staticmethod
    def _decrypt_sensitive(value: str) -> str:
        """Decrypt sensitive values when encrypted marker is present."""
        if not value:
            return value
        if not value.startswith("enc:"):
            return value

        cipher = AuthManager._get_cipher()
        if not cipher:
            return ""

        try:
            return cipher.decrypt(value[4:].encode("utf-8")).decode("utf-8")
        except (InvalidToken, ValueError, TypeError):
            return ""

    @staticmethod
    def _send_verification_email(to_email: str, verification_code: str, username: str) -> dict:
        """Send email verification code through SMTP."""
        if not AuthManager._is_email_configured():
            return {
                "success": False,
                "message": (
                    "Email is not configured on this server. "
                    "Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, and SMTP_PASSWORD."
                )
            }

        smtp_host = AuthManager._get_config_value("SMTP_HOST")
        smtp_port_raw = AuthManager._get_config_value("SMTP_PORT", "587")
        smtp_username = AuthManager._get_config_value("SMTP_USERNAME")
        smtp_password = AuthManager._get_config_value("SMTP_PASSWORD")
        smtp_use_tls = AuthManager._get_config_value("SMTP_USE_TLS", "true").lower() == "true"
        from_email = AuthManager._get_config_value("SMTP_FROM_EMAIL", smtp_username)

        try:
            smtp_port = int(smtp_port_raw)
        except ValueError:
            return {"success": False, "message": "SMTP_PORT must be a valid integer"}

        msg = EmailMessage()
        msg["Subject"] = "TennisPro Verification Code"
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(
            f"""
Hello {username},

Your TennisPro verification code is: {verification_code}

This code expires in 15 minutes.

If you did not request this, you can ignore this email.

TennisPro Team
""".strip()
        )

        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                if smtp_use_tls:
                    server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            return {"success": True, "message": "Verification email sent"}
        except smtplib.SMTPAuthenticationError as e:
            provider_message = ""
            try:
                provider_message = (e.smtp_error or b"").decode("utf-8", errors="ignore").strip()
            except Exception:
                provider_message = str(e)

            if "gmail" in smtp_host.lower():
                return {
                    "success": False,
                    "message": (
                        "SMTP authentication failed for Gmail. Use a Gmail App Password (not your normal password), "
                        "ensure 2-Step Verification is enabled, and set SMTP_USERNAME to the full Gmail address. "
                        f"Provider response: {provider_message}"
                    ),
                }

            return {
                "success": False,
                "message": (
                    "SMTP authentication failed. Verify SMTP_USERNAME/SMTP_PASSWORD and provider security settings. "
                    f"Provider response: {provider_message}"
                ),
            }
        except smtplib.SMTPNotSupportedError:
            return {
                "success": False,
                "message": "SMTP server does not support STARTTLS with current settings. Check SMTP_USE_TLS and provider requirements.",
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to send verification email: {str(e)}"}

    @staticmethod
    def send_test_email(user_id: int) -> dict:
        """Send a test email to the current user for SMTP diagnostics."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "User not found"}

            test_code = AuthManager._generate_verification_code()
            result = AuthManager._send_verification_email(
                to_email=user.email,
                verification_code=test_code,
                username=user.username,
            )
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Test email sent to {user.email}.",
                }
            return result
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def create_user(username: str, email: str, password: str) -> dict:
        """Create a new user account with automatic MFA enabled and automatic email verification."""
        db = SessionLocal()
        try:
            username = normalize_input(username, max_length=50)
            email = normalize_input(email, max_length=254).lower()

            username_valid, username_message = validate_username(username)
            if not username_valid:
                return {"success": False, "message": username_message}

            if not validate_email(email):
                return {"success": False, "message": "Invalid email format"}

            password_valid, password_message = validate_password(password)
            if not password_valid:
                return {"success": False, "message": password_message}

            # Check if user already exists
            existing = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing:
                return {"success": False, "message": "Username or email already exists"}
            
            # Create new user
            password_hash = AuthManager.hash_password(password)
            
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                mfa_enabled=True,  # Automatically enabled
                email_verified=True,
                email_verification_code=None,
                email_code_expires_at=None
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            return {
                "success": True,
                "message": "User created and verified successfully.",
                "user_id": new_user.id,
                "requires_email_verification": False,
                "email_sent": False,
                "verification_code": None
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def _generate_verification_code() -> str:
        """Generate a 6-digit email verification code."""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @staticmethod
    def verify_email_code(user_id: int, code: str) -> dict:
        """Verify MFA/login challenge code."""
        db = SessionLocal()
        try:
            if not AuthManager._check_rate_limit(f"verify_code:{user_id}", limit=10, window_seconds=900):
                return {"success": False, "message": "Too many attempts. Please wait and try again."}

            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Check if a code exists first
            if not user.email_verification_code or not user.email_code_expires_at:
                return {"success": False, "message": "No active verification code. Please resend a code."}

            # Check if code matches and hasn't expired
            code_hash = AuthManager._hash_verification_code(code)
            if not hmac.compare_digest(user.email_verification_code, code_hash):
                return {"success": False, "message": "Invalid verification code"}
            
            if user.email_code_expires_at < datetime.utcnow():
                return {"success": False, "message": "Verification code expired"}
            
            # Mark email as verified
            user.email_verified = True
            user.email_verification_code = None
            user.email_code_expires_at = None
            db.commit()
            
            return {"success": True, "message": "Email verified successfully"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()

    @staticmethod
    def issue_login_mfa_challenge(user_id: int) -> dict:
        """Issue a one-time MFA challenge code for login."""
        db = SessionLocal()
        try:
            if not AuthManager._check_rate_limit(f"issue_mfa:{user_id}", limit=6, window_seconds=900):
                return {"success": False, "message": "Too many MFA requests. Please wait and try again."}

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "User not found"}

            if not user.mfa_enabled:
                return {"success": True, "message": "MFA not enabled", "email_sent": False, "verification_code": None}

            verification_code = AuthManager._generate_verification_code()
            user.email_verification_code = AuthManager._hash_verification_code(verification_code)
            user.email_code_expires_at = datetime.utcnow() + timedelta(minutes=10)
            db.commit()

            email_result = AuthManager._send_verification_email(
                to_email=user.email,
                verification_code=verification_code,
                username=user.username
            )

            email_sent = email_result["success"]
            result_message = (
                "MFA code sent"
                if email_sent
                else f"MFA code generated, but email could not be sent: {email_result['message']}"
            )

            return {
                "success": True,
                "message": result_message,
                "email_sent": email_sent,
                "verification_code": verification_code if not email_sent else None
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def resend_verification_code(user_id: int) -> dict:
        """Resend MFA/login challenge code."""
        db = SessionLocal()
        try:
            if not AuthManager._check_rate_limit(f"resend_code:{user_id}", limit=5, window_seconds=900):
                return {"success": False, "message": "Too many resend attempts. Please wait and try again."}

            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {"success": False, "message": "User not found"}

            if not user.mfa_enabled:
                return {"success": False, "message": "MFA is not enabled for this user"}
            
            # Generate new verification code
            verification_code = AuthManager._generate_verification_code()
            user.email_verification_code = AuthManager._hash_verification_code(verification_code)
            user.email_code_expires_at = datetime.utcnow() + timedelta(minutes=15)
            db.commit()

            email_result = AuthManager._send_verification_email(
                to_email=user.email,
                verification_code=verification_code,
                username=user.username
            )

            email_sent = email_result["success"]
            result_message = (
                "Verification code resent"
                if email_sent
                else f"Code regenerated, but email could not be sent: {email_result['message']}"
            )
            
            return {
                "success": True,
                "message": result_message,
                "email_sent": email_sent,
                "verification_code": verification_code if not email_sent else None
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> dict:
        """Authenticate a user with username and password."""
        db = SessionLocal()
        try:
            username = normalize_input(username, max_length=50)
            login_bucket = f"login:{username.lower()}"
            if not AuthManager._check_rate_limit(login_bucket, limit=8, window_seconds=900):
                return {"success": False, "message": "Too many login attempts. Please try again later."}

            user = db.query(User).filter(User.username == username).first()
            
            if not user or not AuthManager.verify_password(password, user.password_hash):
                return {"success": False, "message": "Invalid username or password"}

            AuthManager._clear_rate_limit(login_bucket)

            # Auto-upgrade legacy unverified users to verified state.
            if not user.email_verified:
                user.email_verified = True
                user.email_verification_code = None
                user.email_code_expires_at = None
                db.commit()
            
            return {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "mfa_enabled": user.mfa_enabled,
                "email_verified": user.email_verified,
                "requires_email_verification": bool(user.mfa_enabled)
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def setup_mfa(user_id: int) -> dict:
        """Setup MFA for a user and return QR code."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Generate secret key
            secret_key = pyotp.random_base32()
            
            # Create provisioning URI for QR code
            totp = pyotp.TOTP(secret_key)
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name="TennisPro"
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Store secret temporarily (not yet enabled)
            user.mfa_secret = AuthManager._encrypt_sensitive(secret_key)
            db.commit()
            
            return {
                "success": True,
                "secret_key": secret_key,
                "qr_code": img_bytes.getvalue()
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def verify_mfa_code(user_id: int, code: str) -> dict:
        """Verify MFA code."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.mfa_secret:
                return {"success": False, "message": "MFA not set up for this user"}

            mfa_secret = AuthManager._decrypt_sensitive(user.mfa_secret)
            if not mfa_secret:
                return {"success": False, "message": "MFA secret is unavailable. Please set up MFA again."}

            totp = pyotp.TOTP(mfa_secret)
            
            # Allow for time drift (current, previous, and next code)
            if not totp.verify(code, valid_window=1):
                return {"success": False, "message": "Invalid MFA code"}
            
            return {"success": True, "message": "MFA code verified"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def enable_mfa(user_id: int) -> dict:
        """Enable MFA for a user."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.mfa_secret:
                return {"success": False, "message": "MFA not set up"}
            
            user.mfa_enabled = True
            db.commit()
            
            return {"success": True, "message": "MFA enabled successfully"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def disable_mfa(user_id: int) -> dict:
        """Disable MFA for a user."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "User not found"}
            
            user.mfa_enabled = False
            user.mfa_secret = None
            db.commit()
            
            return {"success": True, "message": "MFA disabled"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        """Get user information by ID."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "User not found"}
            
            return {
                "success": True,
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "mfa_enabled": user.mfa_enabled,
                "created_at": user.created_at
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()
