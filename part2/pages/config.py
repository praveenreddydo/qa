from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class TrupeerSettings:
    """Runtime configuration. Secrets are supplied only through .env or CI variables."""

    base_url: str
    login_path: str
    auth_mode: str
    storage_state: Path
    cdp_url: str
    chrome_path: str | None
    email: str | None
    password: str | None
    video_url: str | None
    video_title: str | None

    @classmethod
    def from_environment(cls) -> "TrupeerSettings":
        return cls(
            base_url=os.getenv("TRUPEER_BASE_URL", "https://app.trupeer.ai").rstrip("/"),
            login_path=os.getenv("TRUPEER_LOGIN_PATH", "/login"),
            auth_mode=os.getenv("TRUPEER_AUTH_MODE", "password").lower(),
            storage_state=PROJECT_ROOT / os.getenv(
                "TRUPEER_STORAGE_STATE", "part2/.auth/trupeer_google_session.json"
            ),
            cdp_url=os.getenv("TRUPEER_CDP_URL", "http://127.0.0.1:9222"),
            chrome_path=os.getenv("TRUPEER_CHROME_PATH"),
            email=os.getenv("TRUPEER_EMAIL"),
            password=os.getenv("TRUPEER_PASSWORD"),
            video_url=os.getenv("TRUPEER_VIDEO_URL"),
            video_title=os.getenv("TRUPEER_VIDEO_TITLE"),
        )

    @property
    def has_credentials(self) -> bool:
        return bool(self.email and self.password)

    @property
    def uses_google_session(self) -> bool:
        return self.auth_mode == "google_session"

    def require_storage_state(self) -> Path:
        if not self.uses_google_session:
            raise RuntimeError("TRUPEER_AUTH_MODE must be google_session to use a saved Google session.")
        if not self.storage_state.exists():
            raise RuntimeError(
                "Google session file is missing. Run `python -m part2.bootstrap_google_session` first."
            )
        return self.storage_state

    def require_credentials(self) -> tuple[str, str]:
        if not self.has_credentials:
            raise RuntimeError("TRUPEER_EMAIL and TRUPEER_PASSWORD must be set in .env.")
        return self.email or "", self.password or ""

    @staticmethod
    def selector(variable_name: str, fallback: str) -> str:
        """Use a calibrated selector when present, otherwise a semantic fallback."""
        return os.getenv(variable_name, fallback)
