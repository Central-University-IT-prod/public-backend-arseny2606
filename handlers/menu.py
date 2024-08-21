from aiogram import Router, types

from database.database_connector import get_session
from database.models import User
from tools.helpers import get_profile_info
from tools.markups import MenuCallbackFactory, MenuActions, get_profile_keyboard_markup, get_menu_keyboard_markup, \
    get_travels_keyboard_markup
from translations import MENU_TEXT, TRAVEL_TEXT

router = Router()


@router.callback_query(MenuCallbackFactory.filter())
async def handle_menu_callback(callback: types.CallbackQuery, callback_data: MenuCallbackFactory):
    db_session = get_session()
    user_model = db_session.query(User).filter(User.id == callback.from_user.id).first()
    if callback_data.action == MenuActions.PROFILE:
        await callback.message.edit_text(get_profile_info(user_model), reply_markup=get_profile_keyboard_markup())
    if callback_data.action == MenuActions.MENU:
        await callback.message.edit_text(MENU_TEXT, reply_markup=get_menu_keyboard_markup())
    if callback_data.action == MenuActions.TRAVEL:
        await callback.message.edit_text(TRAVEL_TEXT, reply_markup=get_travels_keyboard_markup())
    await callback.answer()
