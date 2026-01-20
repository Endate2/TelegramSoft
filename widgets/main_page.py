from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MainPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()



        main_layout.addSpacing(20)

        main_layout.addSpacing(30)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        self.button_mailing = QPushButton("Рассылка")
        self.button_inviting = QPushButton("Парсинг канала")
        self.button_parsing = QPushButton("Парсинг")

        buttons = [self.button_mailing, self.button_inviting, self.button_parsing]
        for button in buttons:
            button.setFixedSize(120, 40)
            button.setFont(QFont("Arial", 10))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
            buttons_layout.addWidget(button)

        main_layout.addLayout(buttons_layout)
        main_layout.addSpacing(20)

        self.button_mailing.clicked.connect(self.mailing_clicked)
        self.button_inviting.clicked.connect(self.inviting_clicked)
        self.button_parsing.clicked.connect(self.parsing_clicked)

        self.setLayout(main_layout)

    def mailing_clicked(self):
        self.stacked_widget.setCurrentIndex(1)

    def inviting_clicked(self):
        self.stacked_widget.setCurrentIndex(2)

    def parsing_clicked(self):
        self.stacked_widget.setCurrentIndex(3)
