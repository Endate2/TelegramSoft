from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from widgets.main_page import MainPage
from widgets.mailing_page import MailingPage
from widgets.parsing_page_channel import ParsingPageChannel
from widgets.parsing_page import ParsingPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Telegram Bot App")
        self.setFixedSize(600, 400)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_page = MainPage(self.stacked_widget)
        self.mailing_page = MailingPage()
        self.inviting_page = ParsingPageChannel()
        self.parsing_page = ParsingPage()

        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.mailing_page)
        self.stacked_widget.addWidget(self.inviting_page)
        self.stacked_widget.addWidget(self.parsing_page)