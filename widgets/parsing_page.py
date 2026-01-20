# parsing_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                             QLabel, QTextEdit, QHBoxLayout, QMessageBox,
                             QLineEdit, QFormLayout, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ParsingTelegramWorker import ParsingTelegramWorker


class ParsingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.phone = None
        self.password = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Парсинг сообщений из чата")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        auth_layout = QFormLayout()

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Номер телефона (например, +79123456789)")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль (если включена 2FA)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.chat_link_input = QLineEdit()
        self.chat_link_input.setPlaceholderText("Ссылка на чат (например, t.me/username)")

        self.message_count_input = QSpinBox()
        self.message_count_input.setRange(1, 10000)
        self.message_count_input.setValue(100)
        self.message_count_input.setSuffix(" сообщений")

        auth_layout.addRow("Телефон:", self.phone_input)
        auth_layout.addRow("Пароль (2FA):", self.password_input)
        auth_layout.addRow("Ссылка на чат:", self.chat_link_input)
        auth_layout.addRow("Количество сообщений:", self.message_count_input)

        self.content = QTextEdit()
        self.content.setPlaceholderText("Здесь будет отображаться прогресс парсинга...")

        buttons_layout = QHBoxLayout()

        save_auth_button = QPushButton("Сохранить данные")
        save_auth_button.setFixedSize(150, 35)
        save_auth_button.clicked.connect(self.save_auth_data)

        parse_button = QPushButton("Парсить сообщения")
        parse_button.setFixedSize(150, 35)
        parse_button.clicked.connect(self.parse_messages)

        back_button = QPushButton("Назад")
        back_button.setFixedSize(100, 35)

        buttons_layout.addWidget(save_auth_button)
        buttons_layout.addWidget(parse_button)
        buttons_layout.addWidget(back_button)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addLayout(auth_layout)
        layout.addWidget(self.content)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        back_button.clicked.connect(self.go_back)

    def go_back(self):
        self.parent().setCurrentIndex(0)

    def save_auth_data(self):
        self.phone = self.phone_input.text().strip()
        password = self.password_input.text().strip()

        if self.phone:
            QMessageBox.information(self, "Успех", "Данные сохранены!")
            if password:
                self.password = password
                print("Данные аутентификации сохранены")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите номер телефона!")

    def parse_messages(self):
        chat_link = self.chat_link_input.text().strip()
        message_count = self.message_count_input.value()

        if not chat_link:
            QMessageBox.warning(self, "Ошибка", "Введите ссылку на чат!")
            return

        if not self.phone:
            QMessageBox.warning(self, "Ошибка", "Сначала сохраните номер телефона!")
            return

        self.worker = ParsingTelegramWorker("", self.phone, self.password)
        self.worker.set_parsing_mode(chat_link, message_count)
        self.worker.finished.connect(self.on_parsing_finished)
        self.worker.error.connect(self.on_parsing_error)
        self.worker.auth_needed.connect(self.on_auth_needed)
        self.worker.progress.connect(self.on_parsing_progress)
        self.worker.start()

        self.content.setText(f"Начинаем парсинг {message_count} сообщений из чата: {chat_link}\n\n")
        QMessageBox.information(self, "Информация", "Начинаем парсинг сообщений...")

    def on_parsing_progress(self, message):
        current_text = self.content.toPlainText()
        self.content.setText(current_text + message + "\n")
        self.content.verticalScrollBar().setValue(
            self.content.verticalScrollBar().maximum()
        )

    def on_parsing_finished(self, result):
        self.content.setText(self.content.toPlainText() + f"\n{result}\n")
        QMessageBox.information(self, "Успех", result)

    def on_parsing_error(self, error):
        self.content.setText(self.content.toPlainText() + f"\nОшибка: {error}\n")
        QMessageBox.critical(self, "Ошибка", error)

    def on_auth_needed(self):
        QMessageBox.warning(self, "Требуется аутентификация",
                            "Сохраните номер телефона для авторизации!")