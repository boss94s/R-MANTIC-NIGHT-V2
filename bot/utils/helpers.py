from typing import List, Any, Optional
from datetime import datetime


def format_user_info(telegram_id: int, username: Optional[str], first_name: str) -> str:
    if username:
        return f"[{first_name}](tg://user?id={telegram_id}) (@{username})"
    return f"[{first_name}](tg://user?id={telegram_id})"


def paginate(items: List[Any], page: int, per_page: int = 5) -> tuple[List[Any], int]:
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total_pages


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else "—"


def truncate(text: str, max_len: int = 50) -> str:
    return text if len(text) <= max_len else text[:max_len - 3] + "..."


def escape_markdown(text: str) -> str:
    special = r"_*[]()~`>#+-=|{}.!"
    for ch in special:
        text = text.replace(ch, f"\\{ch}")
    return text


def format_number(n: int) -> str:
    return f"{n:,}".replace(",", "،")
