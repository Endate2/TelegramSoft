# ParsingTelegramWorker.py
from PyQt6.QtCore import QThread, pyqtSignal
from telethon import TelegramClient
import asyncio
import pandas as pd
from datetime import datetime
import os
import re


class ParsingTelegramChannelWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    auth_needed = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, message, phone=None, password=None):
        super().__init__()
        self.message = message
        self.phone = phone
        self.password = password
        self.parsing_mode = False
        self.chat_link = None
        self.message_count = None

    def set_parsing_mode(self, chat_link, message_count=100):
        self.parsing_mode = True
        self.chat_link = chat_link
        self.message_count = message_count

    def run(self):
        try:
            if self.parsing_mode:
                asyncio.run(self.parse_chat_messages())
        except Exception as e:
            self.error.emit(f"Ошибка: {e}")

    def extract_telegram_contacts(self, text):
        """Извлекает Telegram контакты вида @username из текста"""
        if not text:
            return ""

        # Ищем паттерны @username
        telegram_pattern = r'@[a-zA-Z][\w]{4,31}'
        contacts = re.findall(telegram_pattern, text)

        # Убираем дубликаты и возвращаем строку с контактами через запятую
        unique_contacts = list(set(contacts))
        return ", ".join(unique_contacts) if unique_contacts else ""

    async def parse_chat_messages(self):
        api_id = '35166373'
        api_hash = '44a89644f866a81082899b5dcf94372e'

        async with TelegramClient('session_name', api_id, api_hash) as client:
            if not await client.is_user_authorized():
                if not self.phone:
                    self.auth_needed.emit()
                    return
                await client.start(phone=self.phone)

            try:
                self.progress.emit(f"Подключаемся к чату: {self.chat_link}")
                chat_entity = await client.get_entity(self.chat_link)

                messages_data = []
                message_count = 0
                start_time = datetime.now()

                self.progress.emit(f"Собираем {self.message_count} последних сообщений...")

                async for message in client.iter_messages(
                        chat_entity,
                        limit=self.message_count
                ):
                    # Извлекаем только Telegram контакты из сообщения
                    telegram_contacts = self.extract_telegram_contacts(message.text)

                    message_info = {
                        'user_id': message.sender_id,
                        'telegram_contacts': telegram_contacts,
                        'original_message': message.text or ''  # Оставляем оригинал для отладки
                    }

                    messages_data.append(message_info)
                    message_count += 1

                    if message_count % 10 == 0:
                        self.progress.emit(f"Обработано {message_count} сообщений")

                if messages_data:
                    filename = await self.save_to_excel(messages_data, chat_entity.title)
                    self.progress.emit(f"Данные сохранены в файл: {filename}")
                    self.finished.emit(
                        f"Парсинг завершен! Обработано {len(messages_data)} сообщений. Файл: {filename}")
                else:
                    self.finished.emit("Не найдено сообщений в чате")

            except Exception as e:
                self.error.emit(f"Ошибка при парсинге: {e}")

    async def save_to_excel(self, messages_data, chat_title):
        os.makedirs('parsing_results', exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_chat_title = "".join(c for c in chat_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"parsing_results/{safe_chat_title}_telegram_contacts_{timestamp}.xlsx"

        # Создаем DataFrame только с нужными данными
        df = pd.DataFrame(messages_data)
        df.to_excel(filename, index=False, engine='openpyxl')

        return filename