from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    waiting_broadcast_message = State()
    waiting_ban_user_id = State()
    waiting_unban_user_id = State()
    waiting_add_admin_id = State()
    waiting_remove_admin_id = State()

    waiting_character_name = State()
    waiting_character_description = State()
    waiting_character_prompt = State()
    waiting_character_avatar = State()
    waiting_character_category = State()
    editing_character_name = State()
    editing_character_description = State()
    editing_character_prompt = State()

    waiting_add_channel = State()
    waiting_setting_value = State()
    waiting_search_user = State()
