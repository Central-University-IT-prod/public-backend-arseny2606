from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from database.database_connector import get_session
from database.models import User
from tools.helpers import get_location_info, get_country, get_city, get_profile_info
from tools.markups import ProfileCallbackFactory, ProfileActions, get_profile_keyboard_markup
from tools.states import EditProfile
from translations import ENTER_BIO, ENTER_CITY, LOCATION_IS_NOT_RECOGNIZED, ENTER_COUNTRY_OR_GEO, SEND_LOCATION, \
    WRONG_AGE, INCORRECT_COUNTRY, INCORRECT_CITY, ENTER_AGE

router = Router()


@router.callback_query(ProfileCallbackFactory.filter())
async def handle_profile_callback(callback: types.CallbackQuery, callback_data: ProfileCallbackFactory,
                                  state: FSMContext):
    if callback_data.action == ProfileActions.EDIT:
        await state.set_state(EditProfile.entering_age)
        await callback.message.edit_text(ENTER_AGE)
    await callback.answer()


@router.message(StateFilter(EditProfile.entering_age))
async def enter_age(message: types.Message, state: FSMContext):
    age = message.text
    if not age.isdigit():
        return await message.answer(WRONG_AGE)
    db_session = get_session()
    user_model = db_session.query(User).filter(User.id == message.from_user.id).first()
    if user_model is None:
        user_model = User(id=message.from_user.id, name=message.from_user.full_name)
    user_model.age = int(age)
    await state.set_state(EditProfile.entering_country)
    db_session.add(user_model)
    db_session.commit()
    markup = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text=SEND_LOCATION, request_location=True)]])
    return await message.answer(ENTER_COUNTRY_OR_GEO, reply_markup=markup)


@router.message(lambda message: message.content_type == "location", StateFilter(EditProfile.entering_country))
async def handle_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    location_info = get_location_info(lat, lon)
    if not location_info.is_ok:
        return await message.answer(LOCATION_IS_NOT_RECOGNIZED, reply_markup=types.ReplyKeyboardRemove())
    db_session = get_session()
    user_model = db_session.query(User).filter(User.id == message.from_user.id).first()
    user_model.country = location_info.country
    user_model.city = location_info.city
    db_session.add(user_model)
    db_session.commit()
    await state.set_state(EditProfile.entering_bio)
    await message.answer(location_info.user_output + "\n\n" + ENTER_BIO, reply_markup=types.ReplyKeyboardRemove())


@router.message(StateFilter(EditProfile.entering_country))
async def handle_country(message: types.Message, state: FSMContext):
    db_session = get_session()
    user_model = db_session.query(User).filter(User.id == message.from_user.id).first()
    try:
        country = get_country(message.text)
    except IndexError:
        return await message.answer(INCORRECT_COUNTRY)
    user_model.country = country
    db_session.add(user_model)
    db_session.commit()
    await state.set_state(EditProfile.entering_city)
    await message.answer(ENTER_CITY, reply_markup=types.ReplyKeyboardRemove())


@router.message(StateFilter(EditProfile.entering_city))
async def handle_city(message: types.Message, state: FSMContext):
    db_session = get_session()
    user_model = db_session.query(User).filter(User.id == message.from_user.id).first()
    try:
        city = get_city(message.text, user_model.country)["name"]
    except (IndexError, KeyError):
        return await message.answer(INCORRECT_CITY)
    user_model.city = city
    db_session.add(user_model)
    db_session.commit()
    await state.set_state(EditProfile.entering_bio)
    await message.answer(ENTER_BIO, reply_markup=types.ReplyKeyboardRemove())


@router.message(StateFilter(EditProfile.entering_bio))
async def handle_bio(message: types.Message, state: FSMContext):
    db_session = get_session()
    user_model = db_session.query(User).filter(User.id == message.from_user.id).first()
    user_model.bio = message.text
    db_session.add(user_model)
    db_session.commit()
    await state.clear()
    await message.answer(get_profile_info(user_model), reply_markup=get_profile_keyboard_markup())
