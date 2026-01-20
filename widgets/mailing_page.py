from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                             QLabel, QTextEdit, QHBoxLayout, QMessageBox,
                             QLineEdit, QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from MallingTelegramWorker import MallingTelegramWorker


class MailingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = MallingTelegramWorker()  # Создаем worker здесь
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Страница рассылки")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        info_label = QLabel(
            "Сообщения берутся из messages.xlsx (текст и голосовые)\n"
            "Аккаунты из accounts.xlsx\n"
            "Получатели из users.xlsx")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: blue;")

        self.log_text = QTextEdit()  # Переименовал для ясности
        self.log_text.setPlaceholderText("Здесь будут логи рассылки")
        self.log_text.setReadOnly(True)  # Сделаем read-only для логов

        buttons_layout = QHBoxLayout()

        send_button = QPushButton("Начать рассылку")
        send_button.setFixedSize(150, 35)
        send_button.clicked.connect(self.start_mailing)

        back_button = QPushButton("Назад")
        back_button.setFixedSize(100, 35)

        buttons_layout.addWidget(send_button)
        buttons_layout.addWidget(back_button)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(info_label)
        layout.addWidget(self.log_text)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        back_button.clicked.connect(self.go_back)

    def go_back(self):
        self.parent().setCurrentIndex(0)

    def start_mailing(self):
        """Запуск рассылки через Telegram"""
        # Очищаем лог перед новой рассылкой
        self.log_text.clear()

        # Подключаем сигналы worker
        self.worker.finished.connect(self.on_mailing_finished)
        self.worker.error.connect(self.on_mailing_error)
        self.worker.auth_needed.connect(self.on_auth_needed)
        self.worker.progress.connect(self.on_progress)

        # Запускаем worker
        self.worker.start()

        self.log_text.append("Начата отправка сообщений...")

    def on_mailing_finished(self, result):
        self.log_text.append(f"✓ {result}")
        QMessageBox.information(self, "Рассылка завершена", result)

    def on_mailing_error(self, error):
        self.log_text.append(f"✗ {error}")
        QMessageBox.critical(self, "Ошибка рассылки", error)

    def on_auth_needed(self, phone):
        self.log_text.append(f"⚠ Требуется аутентификация для аккаунта {phone}")
        QMessageBox.warning(self, "Требуется аутентификация",
                            f"Для аккаунта {phone} требуется аутентификация!\nПроверьте консоль для ввода кода.")

    def on_progress(self, progress):
        self.log_text.append(f"→ {progress}")