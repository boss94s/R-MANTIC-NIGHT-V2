from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    chatting = State()
    selecting_character = State()
    managing_conversations = State()
    renaming_conversation = State()
    waiting_new_conversation_title = State()
