from PyQt6.QtWidgets import QStackedWidget
from windows.home_window import HomePage
from windows.story_window import StoryPage
from windows.survey_window import SurveyPage
from windows.result_window import ResultPage

class AppWindow(QStackedWidget):
    def __init__(self):
        super().__init__()

        # 페이지 등록
        self.addWidget(HomePage(self))
        self.addWidget(StoryPage(self))
        self.addWidget(SurveyPage(self))
        self.addWidget(ResultPage(self))

        self.setCurrentIndex(0)

        # 전체 배경 색 보정
        self.setStyleSheet("""
            QStackedWidget {
                background-color: #F5F7FA;
            }
        """)
