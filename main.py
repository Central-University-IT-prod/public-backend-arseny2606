import asyncio
import logging

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import bot_token, redis_password
from database.database_connector import get_session
from database.models import User
from handlers import profile, menu, registration, travel
from tools.helpers import send_menu
from tools.states import RegisterUser
from translations import REGISTRATION_ENTER_AGE

bot = Bot(token=bot_token)
dp = Dispatcher(storage=RedisStorage(redis=Redis(host="travel_bot_redis", password=redis_password)))
logging.basicConfig(level=logging.ERROR)

main_router = Router()


@main_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    db_session = get_session()
    user_data = db_session.query(User).filter(User.id == message.from_user.id).first()
    await state.clear()
    if user_data is None:
        await state.set_state(RegisterUser.entering_age)
        return await message.answer(REGISTRATION_ENTER_AGE)
    await send_menu(message)


@main_router.message()
async def fallback(message: types.Message, state: FSMContext):
    db_session = get_session()
    user_data = db_session.query(User).filter(User.id == message.from_user.id).first()
    await state.clear()
    if user_data is None:
        await state.set_state(RegisterUser.entering_age)
        return await message.answer(REGISTRATION_ENTER_AGE)
    await send_menu(message)


async def main():
    dp.include_router(profile.router)
    dp.include_router(registration.router)
    dp.include_router(menu.router)
    dp.include_router(travel.router)
    dp.include_router(main_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
