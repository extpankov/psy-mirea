import requests
from bs4 import BeautifulSoup
from config import cookies, headers, params, BOT_TOKEN, CHAT_ID
from datetime import datetime, timedelta
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from aiogram import F
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()


class PsychologistSchedule:
    def __init__(self):
        self.cookies = cookies
        self.headers = headers
        self.params = params

    def get_response(self, date):
        logger.info(f"Fetching schedule for date: {date}")
        data = {
            'flt_duration': '1.0',
            'flt_specialist': '227102',
            'flt_date_from': date,
            'flt_date_to': '',
            'flt_time_to': '22:00',
            'flt_address': '0',
        }

        try:
            response = requests.post('https://lk.mirea.ru/psychologist/', params=self.params, cookies=self.cookies,
                                     headers=self.headers, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            asyncio.create_task(notify_error(e))
            return []

        soup = BeautifulSoup(response.text, 'lxml')
        tbody = soup.find('tbody')

        if tbody is None or tbody.text.strip() == 'Свободных записей нет':
            logger.info(f"No available slots for date: {date}")
            return []

        slots_info = []
        for tr in tbody.find_all('tr'):
            time_range = tr.find_all('td')[2].text
            reserve_link = tr.find('a', class_='btn btn-success btn-xs btn-block')['href']
            slots_info.append((time_range, reserve_link))

        logger.info(f"Found time slots for date {date}: {slots_info}")
        return slots_info


async def notify_error(error):
    message = f"❗Произошла ошибка с парсером: {error}"
    logger.error(f"Sending error notification: {message}")
    await bot.send_message(CHAT_ID, message)


async def check_schedule():
    logger.info("Starting schedule check...")
    scheduler = PsychologistSchedule()
    current_date = datetime.now()
    upcoming_week = [(current_date + timedelta(days=i)).strftime('%d.%m.%Y') for i in range(10)]

    all_slots = {}
    for date in upcoming_week:
        slots = scheduler.get_response(date)
        if slots:
            all_slots[date] = slots

    if os.path.exists('schedule.json'):
        with open('schedule.json', 'r') as file:
            old_data = json.load(file)
    else:
        old_data = {}

    if old_data != all_slots:
        with open('schedule.json', 'w') as file:
            json.dump(all_slots, file, indent=4)
        logger.info("Schedule updated, notifying changes...")
        await notify_changes(old_data, all_slots)
    else:
        logger.info("No changes in schedule detected.")


async def notify_changes(old_data, new_data):
    changes = []
    current_time = datetime.now()
    current_date_str = current_time.strftime('%d.%m.%Y')

    for date, slots in new_data.items():
        old_slots = {slot[0] for slot in old_data.get(date, [])}
        new_slots = {slot[0] for slot in slots}
        added_slots = new_slots - old_slots

        if added_slots:
            for slot in added_slots:
                reserve_link = next(s[1] for s in slots if s[0] == slot)
                start_time_str, end_time_str = slot.split(" - ")
                start_time = datetime.strptime(start_time_str, '%H:%M')
                end_time = datetime.strptime(end_time_str, '%H:%M')

                if date == current_date_str:
                    while start_time < end_time:
                        if start_time > current_time:
                            time_slot = f"{start_time.strftime('%H:%M')} - {(start_time + timedelta(hours=1)).strftime('%H:%M')}"
                            changes.append((date, time_slot, reserve_link))

                        start_time += timedelta(hours=1)
                else:
                    changes.append((date, slot, reserve_link))

    if changes:
        for change in changes:
            if isinstance(change, tuple):
                date, slot, link = change

                date_obj = datetime.strptime(date, '%d.%m.%Y')
                weekday = date_obj.strftime('%A')

                days_of_week = {'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда', 'Thursday': 'Четверг', 'Friday': 'Пятница'}

                keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="Записаться", url=f"https://lk.mirea.ru{link}")
                ]])

                message = f"⚡Добавлены новые записи на {date} ({days_of_week[weekday].lower()}): {slot}"
                logger.info(f"Sending notification with changes: {message}")
                await bot.send_message(CHAT_ID, message, reply_markup=keyboard)
            else:
                logger.info(f"Sending notification with changes: {change}")
                await bot.send_message(CHAT_ID, change)
    else:
        logger.info("No changes to notify.")


async def periodic_check():
    while True:
        await check_schedule()
        await asyncio.sleep(900)


async def on_startup(dispatcher: Dispatcher):
    logger.info("Bot is starting up...")
    asyncio.create_task(periodic_check())


if __name__ == "__main__":
    dp.startup.register(on_startup)
    dp.include_router(router)
    logger.info("Bot is running...")
    dp.run_polling(bot, skip_updates=True)
