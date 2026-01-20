from random import random, choice
import os

from PyQt6.QtCore import QThread, pyqtSignal
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.types import InputMediaUploadedDocument
import asyncio
import pandas as pd


class MallingTelegramWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    auth_needed = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.text_messages = []
        self.voice_messages = []

    def run(self):
        try:
            self.load_messages()
            asyncio.run(self.send_telegram_messages())
        except Exception as e:
            self.error.emit(f"Ошибка: {e}")

    def load_messages(self):
        try:
            texts_df = pd.read_excel('messages.xlsx', sheet_name='text_messages')
            self.text_messages = texts_df['message_text'].dropna().tolist()

            voices_df = pd.read_excel('messages.xlsx', sheet_name='voice_messages')
            self.voice_messages = voices_df['voice_file_path'].dropna().tolist()

            self.progress.emit(
                f"Загружено {len(self.text_messages)} текстовых и {len(self.voice_messages)} голосовых сообщений")

        except Exception as e:
            self.error.emit(f"Ошибка загрузки сообщений: {e}")

    def get_random_message(self):
        if not self.text_messages and not self.voice_messages:
            return None, None

        if self.text_messages and self.voice_messages:
            message_type = 'text'
        elif self.text_messages:
            message_type = 'text'
        else:
            message_type = 'voice'

        if message_type == 'text':
            return choice(self.text_messages), 'text'
        else:
            return choice(self.voice_messages), 'voice'

    async def send_telegram_messages(self):
        accounts = parse_excel_to_dict_list('accounts.xlsx', sheet_name='accounts')

        if not accounts:
            self.error.emit("Не найдены аккаунты в файле accounts.xlsx")
            return

        users = parse_excel_to_dict_list('users.xlsx', sheet_name='users')

        if not users:
            self.error.emit("Не найдены пользователи в файле users.xlsx")
            return

        if not self.text_messages and not self.voice_messages:
            self.error.emit("Не найдены сообщения для отправки")
            return

        self.progress.emit(f"Найдено {len(accounts)} аккаунтов и {len(users)} пользователей")

        total_sent = 0
        total_errors = 0

        for i, account in enumerate(accounts):
            api_id = account.get('api_id')
            api_hash = account.get('api_hash')
            phone = account.get('phone')

            proxy = {
                'proxy_type': account.get('proxy_type'),
                'addr': account.get('proxy_addr'),
                'port': int(account.get('proxy_port')),
                'username': account.get('proxy_username'),
                'password': account.get('proxy_password'),
                'rdns': True
            }

            if not all([api_id, api_hash, phone]):
                self.progress.emit(f"Пропущен аккаунт {i + 1}: отсутствуют обязательные данные")
                continue

            session_name = f"session_{phone}"

            try:
                sent_from_account = await self.process_account(
                    api_id, api_hash, phone, session_name, users, proxy
                )
                total_sent += sent_from_account
                self.progress.emit(f"Аккаунт {phone} отправил {sent_from_account} сообщений")

            except ConnectionError as e:
                total_errors += 1
                self.progress.emit(f"Ошибка подключения через прокси {phone}: {str(e)}")

            except Exception as e:
                total_errors += 1
                self.progress.emit(f"Ошибка в аккаунте {phone}: {str(e)}")

        result_message = f"Рассылка завершена. Отправлено: {total_sent}, Ошибок: {total_errors}"
        self.finished.emit(result_message)

    async def process_account(self, api_id, api_hash, phone, session_name, users, proxy):
        async with TelegramClient(session_name, int(api_id), api_hash, proxy=proxy) as client:
            sent_count = 0
            max_messages = 10
            users_to_remove = []

            for i in range(min(len(users), max_messages)):
                user_data = users[i]
                username = user_data.get('user_name', '').strip()

                if username:
                    try:
                        if username.startswith('@'):
                            username = username[1:]

                        message_content, message_type = self.get_random_message()

                        if not message_content:
                            self.progress.emit("Нет доступных сообщений для отправки")
                            break

                        if message_type == 'text':
                            await client.send_message(username, message_content)
                            self.progress.emit(f"Отправлено текстовое сообщение пользователю {username}")
                        else:
                            if os.path.exists(message_content):
                                await client.send_file(
                                    username,
                                    message_content,
                                    voice_note=True
                                )
                                self.progress.emit(f"Отправлено голосовое сообщение пользователю {username}")
                            else:
                                self.progress.emit(f"Файл голосового сообщения не найден: {message_content}")
                                continue

                        sent_count += 1
                        users_to_remove.append(i)

                        sleep_time = random.randint(50, 60)
                        await asyncio.sleep(sleep_time)

                    except Exception as e:
                        self.progress.emit(f"Ошибка отправки пользователю {username}: {str(e)}")

            for index in sorted(users_to_remove, reverse=True):
                if index < len(users):
                    users.pop(index)

            return sent_count

    async def authenticate_client(self, client, phone):
        await client.send_code_request(phone)

        while True:
            try:
                code = input(f"Введите код для {phone}: ")
                await client.sign_in(phone=phone, code=code)
                break
            except PhoneCodeInvalidError:
                print("Неверный код, попробуйте снова")
            except SessionPasswordNeededError:
                password = input(f"Введите пароль 2FA для {phone}: ")
                await client.sign_in(password=password)
                break


def parse_excel_to_dict_list(filepath: str, sheet_name=None):
    if not os.path.exists(filepath):
        return []

    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        dict_list = df.to_dict(orient='records')
        return dict_list
    except Exception as e:
        print(f"Ошибка чтения файла {filepath}: {e}")
        return []