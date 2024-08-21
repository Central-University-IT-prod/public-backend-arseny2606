from aiogram.fsm.state import StatesGroup, State


class RegisterUser(StatesGroup):
    entering_age = State()
    entering_country = State()
    entering_city = State()
    entering_bio = State()


class EditProfile(StatesGroup):
    entering_age = State()
    entering_country = State()
    entering_city = State()
    entering_bio = State()


class CreateTravel(StatesGroup):
    entering_title = State()


class EditTravel(StatesGroup):
    entering_description = State()


class CreateTravelLocation(StatesGroup):
    entering_location = State()
    entering_start_date = State()
    entering_end_date = State()


class AddUserToTravel(StatesGroup):
    send_user_forward = State()


class CreateTravelNote(StatesGroup):
    upload_file = State()
    choice_visibility = State()
