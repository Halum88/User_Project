import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import os
from datetime import datetime
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from scrapper.get_region import get_region_in_db


load_dotenv()

    

div_log = 'bot/logs_bot/'
log_file = f'bot_{datetime.now().strftime("%d_%m_%Y")}.log'
logging.basicConfig(filename=div_log + log_file, level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')



API_TOKEN = os.environ['API_TOKEN']

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(Command(commands=['start', 'help']))
async def send_welcome(message: types.Message):
    # button start
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Список регионов", callback_data="list_regions")],
        [InlineKeyboardButton(text="Введу сам номер региона", callback_data="enter_region_number")]
    ])
    
    await message.reply("Привет! Выберите один из вариантов:", reply_markup=keyboard)


# button "Список регионов"
@dp.callback_query(lambda c: c.data == "list_regions")
async def send_region_list(call: types.CallbackQuery):
    regions = get_region_in_db()  
    region_list = "\n".join([f"{idx + 1}. {region}" for idx, region in enumerate(regions)])  
    await call.message.answer(region_list)  


# button "Введу сам номер региона"
@dp.callback_query(lambda c: c.data == "enter_region_number")
async def request_region_number(call: types.CallbackQuery):
    await call.message.answer("Введите номер региона:")


@dp.message()
async def handle_region_input(message: types.Message):
    text = message.text.strip()

    if text.isdigit():
        region_number = int(text) 
        region = get_region_in_db(region_number - 1)  
        await message.answer(region) 
    else:
        await message.answer("Пожалуйста, введите номер региона (например, 1).")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)  
    logging.info("Бот успешно запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())