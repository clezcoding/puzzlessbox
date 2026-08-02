"""Google Calendar OAuth + sync (D-17..D-21, D-29, CAL-02, CAL-03)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import text
from sqlmodel import Session, select

from app.core.config import Settings, get_settings
from app.core.security import decrypt_token, encrypt_token
from app.models import CalendarToken, Event

CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _state_key(settings: Settings) -> bytes:
    raw = settings.ENCRYPTION_KEY.encode()
    if len(raw) < 32:
        raw = raw.ljust(32, b"0")
    return raw[:32]


def make_oauth_state(owner_id: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    payload = {"owner_id": owner_id, "nonce": secrets.token_urlsafe(16)}
    raw = json.dumps(payload, sort_keys=True)
    signature = hmac.new(_state_key(settings), raw.encode(), hashlib.sha256).hexdigest()
    token = f"{raw}|{signature}"
    return base64.urlsafe_b64encode(token.encode()).decode()


def verify_oauth_state(state: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    try:
        decoded = base64.urlsafe_b64decode(state.encode()).decode()
        raw, signature = decoded.rsplit("|", 1)
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_OAUTH_STATE", "message": "Malformed OAuth state."},
        ) from exc

    expected = hmac.new(_state_key(settings), raw.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_OAUTH_STATE", "message": "OAuth state signature mismatch."},
        )

    owner_id = json.loads(raw).get("owner_id")
    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_OAUTH_STATE", "message": "OAuth state missing owner."},
        )
    return str(owner_id)


def _client_config(settings: Settings) -> dict[str, Any]:
    return {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }


def concurrency_conflict(etag: str, remote_state: dict[str, Any]) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        detail={
            "code": "CONCURRENCY_CONFLICT",
            "message": "The calendar event has been modified externally.",
            "details": {"etag": etag, "remote_state": remote_state},
        },
    )


class GoogleCalendarService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def create_flow(self, state: str) -> Flow:
        flow = Flow.from_client_config(
            _client_config(self.settings),
            scopes=CALENDAR_SCOPES,
            redirect_uri=self.settings.GOOGLE_REDIRECT_URI,
        )
        flow.oauth2session.state = state
        return flow

    def authorization_url(self, owner_id: str) -> tuple[str, str]:
        state = make_oauth_state(owner_id, self.settings)
        flow = self.create_flow(state)
        url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return url, state

    def exchange_code(self, code: str, state: str) -> tuple[str, Credentials]:
        owner_id = verify_oauth_state(state, self.settings)
        flow = self.create_flow(state)
        flow.fetch_token(code=code)
        credentials = flow.credentials
        if not credentials.token or not credentials.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "OAUTH_TOKEN_ERROR",
                    "message": "Google did not return access and refresh tokens.",
                },
            )
        return owner_id, credentials

    def upsert_tokens(self, db: Session, owner_id: str, credentials: Credentials) -> None:
        now = datetime.now(timezone.utc)
        row = db.get(CalendarToken, uuid.UUID(owner_id))
        if row is None:
            row = CalendarToken(owner_id=uuid.UUID(owner_id))
        row.encrypted_access = encrypt_token(credentials.token)
        row.encrypted_refresh = encrypt_token(credentials.refresh_token)
        row.expires_at = credentials.expiry
        row.updated_at = now
        db.add(row)
        db.commit()

    def _load_credentials(self, db: Session, owner_id: str) -> Credentials:
        row = db.get(CalendarToken, uuid.UUID(owner_id))
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "CALENDAR_NOT_CONNECTED",
                    "message": "Connect Google Calendar before using this endpoint.",
                },
            )
        return Credentials(
            token=decrypt_token(row.encrypted_access),
            refresh_token=decrypt_token(row.encrypted_refresh),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.settings.GOOGLE_CLIENT_ID,
            client_secret=self.settings.GOOGLE_CLIENT_SECRET,
            scopes=CALENDAR_SCOPES,
        )

    def _calendar_service(self, db: Session, owner_id: str):
        credentials = self._load_credentials(db, owner_id)
        return build("calendar", "v3", credentials=credentials, cache_discovery=False)

    def _selected_calendar_id(self, db: Session, owner_id: str) -> str:
        row = db.get(CalendarToken, uuid.UUID(owner_id))
        if row is None or not row.selected_calendar_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "CALENDAR_NOT_SELECTED",
                    "message": "Select a Google calendar before creating events.",
                },
            )
        return row.selected_calendar_id

    def list_calendars(self, db: Session, owner_id: str) -> list[dict[str, Any]]:
        service = self._calendar_service(db, owner_id)
        result = service.calendarList().list().execute()
        return [
            {
                "id": item.get("id"),
                "summary": item.get("summary"),
                "primary": item.get("primary", False),
            }
            for item in result.get("items", [])
        ]

    def select_calendar(self, db: Session, owner_id: str, calendar_id: str) -> None:
        row = db.get(CalendarToken, uuid.UUID(owner_id))
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "CALENDAR_NOT_CONNECTED",
                    "message": "Connect Google Calendar before selecting a calendar.",
                },
            )
        row.selected_calendar_id = calendar_id
        row.updated_at = datetime.now(timezone.utc)
        db.add(row)
        db.commit()

    def disconnect(self, db: Session, owner_id: str) -> None:
        row = db.get(CalendarToken, uuid.UUID(owner_id))
        if row is not None:
            db.delete(row)
            db.commit()

    def connection_status(self, db: Session, owner_id: str) -> dict[str, Any]:
        row = db.get(CalendarToken, uuid.UUID(owner_id))
        if row is None:
            return {"connected": False, "selected_calendar_id": None}
        return {
            "connected": True,
            "selected_calendar_id": row.selected_calendar_id,
        }

    def create_event(
        self,
        db: Session,
        owner_id: str,
        *,
        title: str,
        summary: str,
        starts_at: datetime | None,
        ends_at: datetime | None,
        category_id: uuid.UUID,
    ) -> tuple[Event, dict[str, Any]]:
        calendar_id = self._selected_calendar_id(db, owner_id)
        service = self._calendar_service(db, owner_id)

        body: dict[str, Any] = {
            "summary": title,
            "description": summary,
        }
        if starts_at and ends_at:
            body["start"] = {"dateTime": starts_at.isoformat()}
            body["end"] = {"dateTime": ends_at.isoformat()}

        remote = service.events().insert(calendarId=calendar_id, body=body).execute()
        now = datetime.now(timezone.utc)
        event = Event(
            owner_id=uuid.UUID(owner_id),
            category_id=category_id,
            title=title,
            summary=summary,
            starts_at=starts_at,
            ends_at=ends_at,
            google_event_id=remote.get("id"),
            etag=remote.get("etag"),
            created_at=now,
            updated_at=now,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event, remote

    def get_remote_event(
        self, db: Session, owner_id: str, calendar_id: str, google_event_id: str
    ) -> dict[str, Any]:
        service = self._calendar_service(db, owner_id)
        return (
            service.events()
            .get(calendarId=calendar_id, eventId=google_event_id)
            .execute()
        )

    def update_event_with_etag(
        self,
        db: Session,
        owner_id: str,
        *,
        calendar_id: str,
        google_event_id: str,
        client_etag: str,
        event_body: dict[str, Any],
    ) -> dict[str, Any]:
        service = self._calendar_service(db, owner_id)
        try:
            remote = (
                service.events()
                .get(calendarId=calendar_id, eventId=google_event_id)
                .execute()
            )
        except HttpError as exc:
            raise HTTPException(
                status_code=exc.resp.status,
                detail={
                    "code": "GOOGLE_CALENDAR_ERROR",
                    "message": str(exc),
                },
            ) from exc

        remote_etag = remote.get("etag")
        if client_etag != remote_etag:
            raise concurrency_conflict(remote_etag or "", remote)

        merged = {**remote, **event_body}
        try:
            request = service.events().update(
                calendarId=calendar_id,
                eventId=google_event_id,
                body=merged,
            )
            request.headers["If-Match"] = client_etag
            return request.execute()
        except HttpError as exc:
            if exc.resp.status == 412:
                try:
                    latest = (
                        service.events()
                        .get(calendarId=calendar_id, eventId=google_event_id)
                        .execute()
                    )
                except HttpError:
                    latest = remote
                raise concurrency_conflict(latest.get("etag") or client_etag, latest) from exc
            raise HTTPException(
                status_code=exc.resp.status,
                detail={
                    "code": "GOOGLE_CALENDAR_ERROR",
                    "message": str(exc),
                },
            ) from exc


def events_category_id(db: Session) -> uuid.UUID:
    category_id = db.execute(
        text("SELECT id FROM categories WHERE name = 'Termine' LIMIT 1")
    ).scalar_one_or_none()
    if category_id is None:
        raise RuntimeError("Default Termine category is not seeded")
    return uuid.UUID(str(category_id))


calendar_service = GoogleCalendarService()
