from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import settings
from .models import Click, Link
from .shortcode import RESERVED, generate_code

_MAX_ALLOCATION_ATTEMPTS = 5


class InvalidAlias(Exception):
    pass


class AliasConflict(Exception):
    pass


def create_link(db: Session, target_url: str, custom_alias: Optional[str] = None) -> Link:
    if custom_alias:
        if custom_alias in RESERVED:
            raise InvalidAlias(custom_alias)
        link = Link(code=custom_alias, target_url=target_url)
        db.add(link)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise AliasConflict(custom_alias) from exc
        db.refresh(link)
        return link

    for _ in range(_MAX_ALLOCATION_ATTEMPTS):
        code = generate_code(settings.shortcode_length)
        if code in RESERVED:
            continue
        link = Link(code=code, target_url=target_url)
        db.add(link)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(link)
        return link

    raise RuntimeError("failed to allocate a unique short code")


def get_active_link(db: Session, code: str) -> Optional[Link]:
    return db.scalar(select(Link).where(Link.code == code, Link.is_active.is_(True)))


def count_clicks(db: Session, link_id: int) -> int:
    return db.scalar(select(func.count(Click.id)).where(Click.link_id == link_id)) or 0


def record_click(
    db: Session, link_id: int, referrer: Optional[str], user_agent: Optional[str]
) -> None:
    db.add(Click(link_id=link_id, referrer=referrer, user_agent=user_agent))
    db.commit()


def deactivate_link(db: Session, link: Link) -> None:
    link.is_active = False
    db.commit()


def daily_stats(db: Session, link_id: int, days: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.scalars(select(Click).where(Click.link_id == link_id)).all()
    buckets: dict[str, int] = {}
    for click in rows:
        ts = click.ts if click.ts.tzinfo else click.ts.replace(tzinfo=timezone.utc)
        if ts < cutoff:
            continue
        day = ts.date().isoformat()
        buckets[day] = buckets.get(day, 0) + 1
    return [{"date": day, "clicks": buckets[day]} for day in sorted(buckets)]
