import datetime

from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from database.database_connector import get_session
from database.models import User, Travel, TravelLocation, TravelNote
from tools.helpers import send_travel_info, get_paginated_travel_list, get_paginated_travel_locations_list, \
    get_city_and_country, get_location_info, send_travel_location_info, get_paginated_travel_notes_list, \
    send_travel_note_info
from tools.map_draw import get_trip_route
from tools.markups import TravelMenuCallbackFactory, \
    TravelMenuActions, TravelListPaginationCallbackFactory, TravelListCallbackFactory, TravelCallbackFactory, \
    TravelActions, get_travels_keyboard_markup, TravelLocationsListPaginationCallbackFactory, \
    TravelLocationCreateCallbackFactory, TravelLocationCallbackFactory, TravelLocationActions, \
    TravelNoteListPaginationCallbackFactory, TravelNoteCallbackFactory, TravelNoteActions, \
    TravelNoteCreateCallbackFactory, get_travel_note_visibility_keyboard_markup, TravelNoteVisibilityCallbackFactory, \
    TravelNoteVisibilityActions
from tools.states import CreateTravel, EditTravel, CreateTravelLocation, AddUserToTravel, CreateTravelNote
from translations import ENTER_TRAVEL_TITLE, TRAVEL_TITLE_CONFLICT, TRAVEL_DELETED, TRAVEL_TEXT, \
    ENTER_TRAVEL_DESCRIPTION, ENTER_TRAVEL_LOCATION, ENTER_TRAVEL_LOCATION_START_DATE, ENTER_TRAVEL_LOCATION_END_DATE, \
    WRONG_DATE_FORMAT, LOCATION_IS_NOT_RECOGNIZED, INCORRECT_CITY, ACCESS_DENIED, SEND_USER_FORWARD, \
    SEND_USER_NOT_FORWARDED, SEND_USER_ALREADY_ADDED, NOT_FOUND, SEND_USER_ADDED, UPLOAD_NOTE_FILE, LOADING

router = Router()


@router.callback_query(TravelMenuCallbackFactory.filter())
async def handle_travel_menu_callback(callback: types.CallbackQuery, callback_data: TravelMenuCallbackFactory,
                                      state: FSMContext):
    message = await callback.message.answer(LOADING)
    if callback_data.action == TravelMenuActions.CREATE:
        await state.set_state(CreateTravel.entering_title)
        await callback.message.edit_text(ENTER_TRAVEL_TITLE)
    if callback_data.action == TravelMenuActions.LIST:
        db_session = get_session()
        user_model = db_session.query(User).filter(User.id == callback.from_user.id).first()
        text, markup = get_paginated_travel_list(user_model)
        await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()
    await message.delete()


@router.callback_query(TravelListPaginationCallbackFactory.filter())
async def handle_travel_list_pagination_callback(callback: types.CallbackQuery,
                                                 callback_data: TravelListPaginationCallbackFactory):
    message = await callback.message.answer(LOADING)
    db_session = get_session()
    user_model = db_session.query(User).filter(User.id == callback.from_user.id).first()
    text, markup = get_paginated_travel_list(user_model, callback_data.offset)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()
    await message.delete()


@router.callback_query(TravelListCallbackFactory.filter())
async def handle_travel_list_callback(callback: types.CallbackQuery, callback_data: TravelListCallbackFactory):
    message = await callback.message.answer(LOADING)
    db_session = get_session()
    travel_model = db_session.query(Travel).filter(Travel.id == callback_data.travel_id).first()
    await send_travel_info(callback, travel_model)
    await callback.answer()
    await message.delete()


@router.callback_query(TravelCallbackFactory.filter())
async def handle_travel_callback(callback: types.CallbackQuery, callback_data: TravelCallbackFactory,
                                 state: FSMContext):
    message = await callback.message.answer(LOADING)
    db_session = get_session()
    travel_model = db_session.query(Travel).filter(Travel.id == callback_data.travel_id).first()
    user_model = db_session.query(User).filter(User.id == callback.from_user.id).first()
    if callback_data.action == TravelActions.ADD_USER:
        if travel_model.owner_id != callback.from_user.id:
            await message.delete()
            return await callback.answer(ACCESS_DENIED)
        await state.set_state(AddUserToTravel.send_user_forward)
        await state.set_data({"travel_id": callback_data.travel_id})
        await callback.message.edit_text(SEND_USER_FORWARD)
        await callback.answer()
    if callback_data.action == TravelActions.DELETE:
        if travel_model.owner_id != callback.from_user.id:
            await message.delete()
            return await callback.answer(ACCESS_DENIED)
        db_session.delete(travel_model)
        db_session.commit()
        await callback.answer(TRAVEL_DELETED)
        await callback.message.edit_text(TRAVEL_TEXT, reply_markup=get_travels_keyboard_markup())
    if callback_data.action == TravelActions.EDIT:
        if travel_model.owner_id != callback.from_user.id:
            await message.delete()
            return await callback.answer(ACCESS_DENIED)
        await state.set_state(EditTravel.entering_description)
        await state.set_data({"travel_id": callback_data.travel_id})
        await callback.message.edit_text(ENTER_TRAVEL_DESCRIPTION)
        await callback.answer()
    if callback_data.action == TravelActions.EDIT_POINTS:
        if callback.from_user.id != travel_model.owner_id and callback.from_user.id not in [user.id for user in
                                                                                            travel_model.access_users]:
            await message.delete()
            return await callback.answer(ACCESS_DENIED)
        text, markup = get_paginated_travel_locations_list(user_model, travel_model)
        await callback.message.edit_text(text, reply_markup=markup)
        await callback.answer()
    if callback_data.action == TravelActions.SHOW_ROUTE:
        if callback.from_user.id != travel_model.owner_id and callback.from_user.id not in [user.id for user in
                                                                                            travel_model.access_users]:
            await message.delete()
            return await callback.answer(ACCESS_DENIED)
        if len(travel_model.locations) >= 1:
            file = get_trip_route(travel_model, user_model)
            if file is None:
                await callback.answer("Маршрут не может быть построен. Вы уже находитесь в стартовой точке маршрута.")
            else:
                await callback.message.answer_photo(BufferedInputFile(file.read(), filename="map.png"))
                file.close()
                await callback.message.delete()
                await send_travel_info(callback, travel_model)
        await callback.answer()
    if callback_data.action == TravelActions.SHOW_NOTES:
        if callback.from_user.id != travel_model.owner_id and callback.from_user.id not in [user.id for user in
                                                                                            travel_model.access_users]:
            await message.delete()
            return await callback.answer(ACCESS_DENIED)
        text, markup = get_paginated_travel_notes_list(user_model, travel_model)
        await callback.message.edit_text(text, reply_markup=markup)
        await callback.answer()
    await message.delete()


@router.callback_query(TravelLocationsListPaginationCallbackFactory.filter())
async def handle_travel_locations_list_pagination_callback(callback: types.CallbackQuery,
                                                           callback_data: TravelLocationsListPaginationCallbackFactory):
    message = await callback.message.answer(LOADING)
    db_session = get_session()
    travel_model = db_session.query(Travel).filter(Travel.id == callback_data.travel_id).first()
    user_model = db_session.query(User).filter(User.id == callback.from_user.id).first()
    if travel_model.owner_id != callback.from_user.id or callback.from_user.id not in [user.id for user in
                                                                                       travel_model.access_users]:
        return await callback.answer(ACCESS_DENIED)
    text, markup = get_paginated_travel_locations_list(user_model, travel_model, callback_data.offset)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()
    await message.delete()


@router.callback_query(TravelLocationCreateCallbackFactory.filter())
async def handle_travel_location_create_callback(callback: types.CallbackQuery,
                                                 callback_data: TravelLocationCreateCallbackFactory, state: FSMContext):
    message = await callback.message.answer(LOADING)
    db_session = get_session()
    travel_model = db_session.query(Travel).filter(Travel.id == callback_data.travel_id).first()
    if travel_model.owner_id != callback.from_user.id:
        return await callback.answer(ACCESS_DENIED)
    await state.set_state(CreateTravelLocation.entering_location)
    await state.set_data({"travel_id": callback_data.travel_id})
    await callback.message.edit_text(ENTER_TRAVEL_LOCATION)
    await callback.answer()
    await message.delete()


@router.callback_query(TravelLocationCallbackFactory.filter())
async def handle_travel_location_callback(callback: types.CallbackQuery, callback_data: TravelLocationCallbackFactory):
    message = await callback.message.answer(LOADING)
    db_session = get_session()
    travel_location = db_session.query(TravelLocation).filter(
        TravelLocation.id == callback_data.location_id).first()
    if travel_location is None:
        await message.delete()
        return await callback.answer(NOT_FOUND)
    if callback_data.action == TravelLocationActions.DELETE:
        travel_model = travel_location.travel
        if travel_model.owner_id != callback.from_user.id:
            await message.delete()
            return await callback.answer(ACCESS_DENIED)
        db_session.delete(travel_location)
        db_session.commit()
        user_model = db_session.query(User).filter(User.id == callback.from_user.id).first()
        text, markup = get_paginated_travel_locations_list(user_model, travel_model)
        await callback.message.edit_text(text, reply_markup=markup)
        await callback.answer()
    if callback_data.action == TravelLocationActions.SHOW:
        if callback.from_user.id != travel_location.travel.owner_id and callback.from_user.id not in [user.id for user
                                                                                                      in
                                                                                                      travel_location.travel.access_users]:
            await message.delete()
            return await callback.answer(ACCESS_DENIED)
        await send_travel_location_info(callback, travel_location)
        await callback.answer()
    await message.delete()


@router.callback_query(TravelNoteListPaginationCallbackFactory.filter())
async def handle_travel_note_list_pagination_callback(callback: types.CallbackQuery,
                                                      callback_data: TravelNoteListPaginationCallbackFactory):
    message = await callback.message.answer(LOADING)
    db_session = get_session()
    travel_model = db_session.query(Travel).filter(Travel.id == callback_data.travel_id).first()
    user_model = db_session.query(User).filter(User.id == callback.from_user.id).first()
    if travel_model.owner_id != callback.from_user.id or callback.from_user.id not in [user.id for user in
                                                                                       travel_model.access_users]:
        await message.delete()
        return await callback.answer(ACCESS_DENIED)
    text, markup = get_paginated_travel_notes_list(user_model, travel_model, callback_data.offset)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()
    await message.delete()


@router.callback_query(TravelNoteCallbackFactory.filter())
async def handle_travel_note_callback(callback: types.CallbackQuery, callback_data: TravelNoteCallbackFactory):
    message = await callback.message.answer(LOADING)
    db_session = get_session()
    travel_note = db_session.query(TravelNote).filter(TravelNote.id == callback_data.note_id).first()
    if travel_note is None:
        await message.delete()
        return await callback.answer(NOT_FOUND)
    if callback_data.action == TravelNoteActions.DELETE:
        travel_model = travel_note.travel
        if travel_model.owner_id != callback.from_user.id:
            await message.delete()
            return await callback.answer(ACCESS_DENIED)
        db_session.delete(travel_note)
        db_session.commit()
        user_model = db_session.query(User).filter(User.id == callback.from_user.id).first()
        text, markup = get_paginated_travel_notes_list(user_model, travel_model)
        await callback.message.answer(text, reply_markup=markup)
        await callback.message.delete()
        await callback.answer()
    if callback_data.action == TravelNoteActions.SHOW:
        if callback.from_user.id != travel_note.travel.owner_id and callback.from_user.id not in [user.id for user in
                                                                                                  travel_note.travel.access_users] \
                or (callback.from_user.id != travel_note.travel.owner_id and not travel_note.is_public):
            await message.delete()
            return await callback.answer(ACCESS_DENIED)
        await send_travel_note_info(callback, travel_note)
        await callback.answer()
    await message.delete()


@router.callback_query(TravelNoteCreateCallbackFactory.filter())
async def handle_travel_note_create_callback(callback: types.CallbackQuery,
                                             callback_data: TravelNoteCreateCallbackFactory, state: FSMContext):
    message = await callback.message.answer(LOADING)
    db_session = get_session()
    travel_model = db_session.query(Travel).filter(Travel.id == callback_data.travel_id).first()
    if travel_model.owner_id != callback.from_user.id:
        await message.delete()
        return await callback.answer(ACCESS_DENIED)
    await state.set_state(CreateTravelNote.upload_file)
    await state.set_data({"travel_id": callback_data.travel_id})
    await callback.message.edit_text(UPLOAD_NOTE_FILE)
    await callback.answer()
    await message.delete()


@router.callback_query(TravelNoteVisibilityCallbackFactory.filter(), StateFilter(CreateTravelNote.choice_visibility))
async def handle_travel_note_visibility_callback(callback: types.CallbackQuery,
                                                 callback_data: TravelNoteVisibilityCallbackFactory, state: FSMContext):
    message = await callback.message.answer(LOADING)
    db_session = get_session()
    travel_note = db_session.query(TravelNote).filter(
        TravelNote.id == (await state.get_data())["note_id"]).first()
    if travel_note is None:
        await message.delete()
        return await callback.answer(NOT_FOUND)
    if travel_note.travel.owner_id != callback.from_user.id:
        await message.delete()
        return await callback.answer(ACCESS_DENIED)
    travel_note.is_public = callback_data.action == TravelNoteVisibilityActions.PUBLIC
    db_session.add(travel_note)
    db_session.commit()
    db_session.refresh(travel_note)
    await state.clear()
    await send_travel_note_info(callback, travel_note)
    await callback.answer()
    await message.delete()


@router.message(StateFilter(CreateTravel.entering_title))
async def enter_title(message: types.Message, state: FSMContext):
    db_session = get_session()
    user_model = db_session.query(User).filter(User.id == message.from_user.id).first()
    travel_model = Travel(title=message.text, owner=user_model)
    db_session.add(travel_model)
    try:
        db_session.commit()
    except:
        return await message.answer(TRAVEL_TITLE_CONFLICT)
    db_session.refresh(travel_model)
    await state.clear()
    await send_travel_info(message, travel_model)


@router.message(StateFilter(EditTravel.entering_description))
async def enter_description(message: types.Message, state: FSMContext):
    db_session = get_session()
    travel_model = db_session.query(Travel).filter(Travel.id == (await state.get_data())["travel_id"]).first()
    travel_model.description = message.text
    db_session.commit()
    await state.clear()
    await send_travel_info(message, travel_model)


@router.message(lambda message: message.content_type == "location", StateFilter(CreateTravelLocation.entering_location))
async def handle_location(message: types.Message, state: FSMContext):
    db_session = get_session()
    travel_location = TravelLocation(travel_id=(await state.get_data())["travel_id"])
    try:
        location_info = get_location_info(message.location.latitude, message.location.longitude)
    except IndexError:
        return await message.answer(LOCATION_IS_NOT_RECOGNIZED)
    if location_info.city is None:
        return await message.answer(LOCATION_IS_NOT_RECOGNIZED)
    travel_location.city = location_info.city
    travel_location.latitude = message.location.latitude
    travel_location.longitude = message.location.longitude
    db_session.add(travel_location)
    db_session.commit()
    await state.set_state(CreateTravelLocation.entering_start_date)
    await state.set_data({"location_id": travel_location.id})
    await message.answer(ENTER_TRAVEL_LOCATION_START_DATE)


@router.message(StateFilter(CreateTravelLocation.entering_location))
async def enter_location(message: types.Message, state: FSMContext):
    db_session = get_session()
    travel_location = TravelLocation(travel_id=(await state.get_data())["travel_id"])
    try:
        city_info = get_city_and_country(message.text)
    except IndexError:
        return await message.answer(INCORRECT_CITY)
    travel_location.city = city_info["name"]
    travel_location.latitude = city_info["lat"]
    travel_location.longitude = city_info["lon"]
    db_session.add(travel_location)
    db_session.commit()
    await state.set_state(CreateTravelLocation.entering_start_date)
    await state.set_data({"location_id": travel_location.id})
    await message.answer(ENTER_TRAVEL_LOCATION_START_DATE)


@router.message(StateFilter(CreateTravelLocation.entering_start_date))
async def enter_start_date(message: types.Message, state: FSMContext):
    db_session = get_session()
    travel_location = db_session.query(TravelLocation).filter(
        TravelLocation.id == (await state.get_data())["location_id"]).first()
    try:
        travel_location.start_date = datetime.datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        return await message.answer(WRONG_DATE_FORMAT)
    db_session.add(travel_location)
    db_session.commit()
    await state.set_state(CreateTravelLocation.entering_end_date)
    await message.answer(ENTER_TRAVEL_LOCATION_END_DATE)


@router.message(StateFilter(CreateTravelLocation.entering_end_date))
async def enter_end_date(message: types.Message, state: FSMContext):
    db_session = get_session()
    travel_location = db_session.query(TravelLocation).filter(
        TravelLocation.id == (await state.get_data())["location_id"]).first()
    try:
        travel_location.end_date = datetime.datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        return await message.answer(WRONG_DATE_FORMAT)
    db_session.add(travel_location)
    db_session.commit()
    db_session.refresh(travel_location)
    await state.clear()
    await send_travel_location_info(message, travel_location)


@router.message(StateFilter(AddUserToTravel.send_user_forward), F.forward_from)
async def send_user_forward(message: types.Message, state: FSMContext):
    db_session = get_session()
    travel_model = db_session.query(Travel).filter(Travel.id == (await state.get_data())["travel_id"]).first()
    user_model = db_session.query(User).filter(User.id == message.forward_from.id).first()
    if user_model is None or travel_model.owner_id == user_model.id:
        return await message.answer(SEND_USER_NOT_FORWARDED)
    travel_model.access_users.append(user_model)
    db_session.add(travel_model)
    try:
        db_session.commit()
    except:
        await message.answer(SEND_USER_ALREADY_ADDED)
        await state.clear()
        db_session.rollback()
        await send_travel_info(message, travel_model)
        return
    for user in travel_model.access_users:
        await message.bot.send_message(user.id, SEND_USER_ADDED.format(user_model=user_model, travel=travel_model),
                                       parse_mode="html")
    await state.clear()
    await send_travel_info(message, travel_model)


@router.message(StateFilter(AddUserToTravel.send_user_forward))
async def send_user_not_forward(message: types.Message):
    await message.answer(SEND_USER_NOT_FORWARDED)


@router.message(StateFilter(CreateTravelNote.upload_file), F.document)
async def upload_file(message: types.Message, state: FSMContext):
    db_session = get_session()
    travel_note = TravelNote(travel_id=(await state.get_data())["travel_id"], file_name=message.document.file_name,
                             file_id=message.document.file_id)
    db_session.add(travel_note)
    db_session.commit()
    db_session.refresh(travel_note)
    await state.set_state(CreateTravelNote.choice_visibility)
    await state.set_data({"note_id": travel_note.id})
    await message.answer("Выбери видимость заметки.",
                         reply_markup=get_travel_note_visibility_keyboard_markup(travel_note.id))


@router.message(StateFilter(CreateTravelNote.upload_file))
async def upload_file(message: types.Message):
    await message.answer(UPLOAD_NOTE_FILE)
