from PyQt6.QtWidgets import QStackedWidget
from windows.home_window import HomePage
from windows.story_window import StoryPage
from windows.survey_window import SurveyPage
from windows.result_window import ResultPage
from windows.pca_window import PCAAdvisorPage
from windows.help_window import HelpPage
from windows.explain_window import ExplainPage
#done



class AppWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.addWidget(HomePage(self))
        self.addWidget(StoryPage(self))
        self.addWidget(SurveyPage(self))
        self.addWidget(ResultPage(self))
        self.addWidget(PCAAdvisorPage(self))
        self.addWidget(HelpPage(self))
        self.addWidget(ExplainPage(self))
        self.setCurrentIndex(0)
        self.setStyleSheet("""
            QStackedWidget {
                background-color: #F5F7FA;
            }
        """)
