from enum import Enum
from typing import Literal

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import Travel, TravelLocation, TravelNote


class MenuActions(Enum):
    PROFILE = "profile"
    TRAVEL = "travel"
    MENU = "menu"


class MenuCallbackFactory(CallbackData, prefix="menu"):
    action: MenuActions


def get_menu_keyboard_markup():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Профиль", callback_data=MenuCallbackFactory(action=MenuActions.PROFILE)
    )
    builder.button(
        text="Путешествия", callback_data=MenuCallbackFactory(action=MenuActions.TRAVEL)
    )
    return builder.as_markup()


class ProfileActions(Enum):
    EDIT = "edit"


class ProfileCallbackFactory(CallbackData, prefix="profile"):
    action: ProfileActions


def get_profile_keyboard_markup():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Редактировать", callback_data=ProfileCallbackFactory(action=ProfileActions.EDIT)
    )
    builder.button(
        text="Меню", callback_data=MenuCallbackFactory(action=MenuActions.MENU)
    )
    builder.adjust(1)
    return builder.as_markup()


class TravelMenuActions(Enum):
    CREATE = "create"
    LIST = "list"


class TravelMenuCallbackFactory(CallbackData, prefix="travel_menu"):
    action: TravelMenuActions


def get_travels_keyboard_markup():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Создать", callback_data=TravelMenuCallbackFactory(action=TravelMenuActions.CREATE)
    )
    builder.button(
        text="Список", callback_data=TravelMenuCallbackFactory(action=TravelMenuActions.LIST)
    )
    builder.button(
        text="Меню", callback_data=MenuCallbackFactory(action=MenuActions.MENU)
    )
    builder.adjust(1)
    return builder.as_markup()


class TravelActions(Enum):
    EDIT_POINTS = "edit_points"
    EDIT = "edit"
    DELETE = "delete"
    SHOW_ROUTE = "show_route"
    ADD_USER = "add_user"
    SHOW_NOTES = "show_notes"


class TravelCallbackFactory(CallbackData, prefix="travel"):
    action: TravelActions
    travel_id: int


def get_travel_info_keyboard_markup(travel_model, is_owner):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Список точек", callback_data=TravelCallbackFactory(action=TravelActions.EDIT_POINTS,
                                                                 travel_id=travel_model.id)
    )
    if len(travel_model.locations) >= 1:
        builder.button(
            text="Маршрут до первой точки", callback_data=TravelCallbackFactory(action=TravelActions.SHOW_ROUTE,
                                                                                travel_id=travel_model.id)
        )
    builder.button(
        text="Заметки", callback_data=TravelCallbackFactory(action=TravelActions.SHOW_NOTES,
                                                            travel_id=travel_model.id)
    )
    if is_owner:
        builder.button(
            text="Добавить пользователя", callback_data=TravelCallbackFactory(action=TravelActions.ADD_USER,
                                                                              travel_id=travel_model.id)
        )
        builder.button(
            text="Редактировать", callback_data=TravelCallbackFactory(action=TravelActions.EDIT,
                                                                      travel_id=travel_model.id)
        )
        builder.button(
            text="Удалить", callback_data=TravelCallbackFactory(action=TravelActions.DELETE,
                                                                travel_id=travel_model.id)
        )
    builder.button(
        text="Меню", callback_data=MenuCallbackFactory(action=MenuActions.TRAVEL)
    )
    builder.adjust(1)
    return builder.as_markup()


class TravelListCallbackFactory(CallbackData, prefix="travel_list"):
    action: Literal["show"] = "show"
    travel_id: int


class TravelListPaginationCallbackFactory(CallbackData, prefix="travel_list_pagination"):
    action: Literal["new_offset"] = "new_offset"
    offset: int


def get_travel_list_keyboard_markup(travel_list: list[Travel], offset_left: int, offset_right: int):
    builder = InlineKeyboardBuilder()
    sizes = []
    for travel in travel_list:
        builder.button(
            text=f"{travel.title} | {travel.owner.name}",
            callback_data=TravelListCallbackFactory(travel_id=travel.id)
        )
        sizes.append(1)
    sizes.append(0)
    if offset_left != -1:
        builder.button(
            text="⬅️",
            callback_data=TravelListPaginationCallbackFactory(offset=offset_left)
        )
        sizes[-1] += 1
    if offset_right != -1:
        builder.button(
            text="➡️",
            callback_data=TravelListPaginationCallbackFactory(offset=offset_right)
        )
        sizes[-1] += 1
    if sizes[-1] == 0:
        sizes.pop()
    builder.button(
        text="Меню путешествий", callback_data=MenuCallbackFactory(action=MenuActions.TRAVEL)
    )
    sizes.append(1)
    builder.adjust(*sizes)
    return builder.as_markup()


class TravelLocationCreateCallbackFactory(CallbackData, prefix="travel_location_create"):
    action: Literal["create"] = "create"
    travel_id: int


class TravelLocationActions(Enum):
    SHOW = "show"
    DELETE = "delete"


class TravelLocationCallbackFactory(CallbackData, prefix="travel_location"):
    action: TravelLocationActions
    location_id: int


class TravelLocationsListPaginationCallbackFactory(CallbackData, prefix="travel_location_list_pagination"):
    action: Literal["new_offset"] = "new_offset"
    offset: int
    travel_id: int


def get_travel_locations_list_keyboard_markup(travel_id: int, locations_list: list[TravelLocation], offset_left: int,
                                              offset_right: int, is_owner: bool):
    builder = InlineKeyboardBuilder()
    sizes = [1]
    if is_owner:
        builder.button(text="Создать", callback_data=TravelLocationCreateCallbackFactory(travel_id=travel_id))
    else:
        sizes.pop()
    for location in locations_list:
        builder.button(
            text=f"{location.city} | {location.start_date} - {location.end_date}",
            callback_data=TravelLocationCallbackFactory(location_id=location.id, action=TravelLocationActions.SHOW)
        )
        sizes.append(1)
    sizes.append(0)
    if offset_left != -1:
        builder.button(
            text="⬅️",
            callback_data=TravelLocationsListPaginationCallbackFactory(offset=offset_left, travel_id=travel_id)
        )
        sizes[-1] += 1
    if offset_right != -1:
        builder.button(
            text="➡️",
            callback_data=TravelLocationsListPaginationCallbackFactory(offset=offset_right, travel_id=travel_id)
        )
        sizes[-1] += 1
    if sizes[-1] == 0:
        sizes.pop()
    builder.button(
        text="Путешествие", callback_data=TravelListCallbackFactory(travel_id=travel_id)
    )
    sizes.append(1)
    builder.adjust(*sizes)
    return builder.as_markup()


def get_travel_location_info_keyboard_markup(location_model: TravelLocation, is_owner: bool):
    builder = InlineKeyboardBuilder()
    if is_owner:
        builder.button(
            text="Удалить",
            callback_data=TravelLocationCallbackFactory(location_id=location_model.id,
                                                        action=TravelLocationActions.DELETE)
        )
    builder.button(
        text="Путешествие", callback_data=TravelListCallbackFactory(travel_id=location_model.travel_id)
    )
    builder.adjust(1)
    return builder.as_markup()


class TravelNoteActions(Enum):
    DELETE = "delete"
    SHOW = "show"


class TravelNoteCallbackFactory(CallbackData, prefix="travel_note"):
    action: TravelNoteActions
    note_id: int


class TravelNoteListPaginationCallbackFactory(CallbackData, prefix="travel_note_list_pagination"):
    action: Literal["new_offset"] = "new_offset"
    offset: int
    travel_id: int


class TravelNoteCreateCallbackFactory(CallbackData, prefix="travel_note_create"):
    action: Literal["create"] = "create"
    travel_id: int


def get_travel_notes_list_keyboard_markup(travel_id: int, notes_list: list[TravelNote], offset_left: int,
                                          offset_right: int, is_owner: bool):
    builder = InlineKeyboardBuilder()
    sizes = [1]
    if is_owner:
        builder.button(text="Создать", callback_data=TravelNoteCreateCallbackFactory(travel_id=travel_id))
    else:
        sizes.pop()
    for note in notes_list:
        builder.button(
            text=f"{note.file_name}",
            callback_data=TravelNoteCallbackFactory(note_id=note.id, action=TravelNoteActions.SHOW)
        )
        sizes.append(1)
    sizes.append(0)
    if offset_left != -1:
        builder.button(
            text="⬅️",
            callback_data=TravelNoteListPaginationCallbackFactory(offset=offset_left, travel_id=travel_id)
        )
        sizes[-1] += 1
    if offset_right != -1:
        builder.button(
            text="➡️",
            callback_data=TravelNoteListPaginationCallbackFactory(offset=offset_right, travel_id=travel_id)
        )
        sizes[-1] += 1
    if sizes[-1] == 0:
        sizes.pop()
    builder.button(
        text="Путешествие", callback_data=TravelListCallbackFactory(travel_id=travel_id)
    )
    sizes.append(1)
    builder.adjust(*sizes)
    return builder.as_markup()


def get_travel_note_info_keyboard_markup(note_model: TravelNote, is_owner: bool):
    builder = InlineKeyboardBuilder()
    if is_owner:
        builder.button(
            text="Удалить",
            callback_data=TravelNoteCallbackFactory(note_id=note_model.id,
                                                    action=TravelNoteActions.DELETE)
        )
    builder.button(
        text="Путешествие", callback_data=TravelListCallbackFactory(travel_id=note_model.travel_id)
    )
    builder.adjust(1)
    return builder.as_markup()


class TravelNoteVisibilityActions(Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class TravelNoteVisibilityCallbackFactory(CallbackData, prefix="travel_note_visibility"):
    action: TravelNoteVisibilityActions
    note_id: int


def get_travel_note_visibility_keyboard_markup(note_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Приватная",
        callback_data=TravelNoteVisibilityCallbackFactory(note_id=note_id,
                                                          action=TravelNoteVisibilityActions.PRIVATE)
    )
    builder.button(
        text="Публичная",
        callback_data=TravelNoteVisibilityCallbackFactory(note_id=note_id,
                                                          action=TravelNoteVisibilityActions.PUBLIC)
    )
    builder.adjust(1)
    return builder.as_markup()
