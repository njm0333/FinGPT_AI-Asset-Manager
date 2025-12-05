from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt
from styles import apply_global_style


class SurveyPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        title = QLabel("투자 성향 설문")
        title.setObjectName("title")

        info = QLabel("아래 문항을 통해 투자성향을 분석합니다.\n(예시 화면)")
        info.setObjectName("subtitle")

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout()

        q1 = QLabel("Q1. 당신의 투자 목적은 무엇인가요?")
        q2 = QLabel("Q2. 위험을 감수할 수 있는 수준은?")
        q3 = QLabel("Q3. 투자 기간은 보통 얼마나 잡나요?")

        for q in (q1, q2, q3):
            q.setStyleSheet("font-size: 15px; margin-bottom: 12px;")
            card_layout.addWidget(q)

        card.setLayout(card_layout)

        next_btn = QPushButton("다음 →")
        next_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        next_btn.setFixedWidth(200)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(card)
        layout.addWidget(next_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addStretch()

        self.setLayout(layout)
        apply_global_style(self)
