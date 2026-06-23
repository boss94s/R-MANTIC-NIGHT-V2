from .main_kb import user_main_kb, back_to_main_kb
from .characters_kb import characters_select_kb, character_confirm_kb
from .conversations_kb import conversations_kb, conversation_detail_kb

user_keyboards = {
    "main": user_main_kb,
}

__all__ = [
    "user_main_kb", "back_to_main_kb",
    "characters_select_kb", "character_confirm_kb",
    "conversations_kb", "conversation_detail_kb",
    "user_keyboards"
]
