from .main_kb import admin_main_kb
from .characters_kb import (
    characters_list_kb, character_detail_kb,
    character_create_confirm_kb, characters_manage_kb
)
from .users_kb import users_manage_kb, user_detail_kb
from .admins_kb import admins_manage_kb
from .channels_kb import channels_manage_kb, channels_list_kb
from .broadcast_kb import broadcast_target_kb
from .settings_kb import settings_kb

admin_keyboards = {
    "main": admin_main_kb,
    "characters": characters_list_kb,
    "users": users_manage_kb,
}

__all__ = [
    "admin_main_kb", "characters_list_kb", "character_detail_kb",
    "character_create_confirm_kb", "characters_manage_kb",
    "users_manage_kb", "user_detail_kb", "admins_manage_kb",
    "channels_manage_kb", "channels_list_kb", "broadcast_target_kb",
    "settings_kb", "admin_keyboards"
]
