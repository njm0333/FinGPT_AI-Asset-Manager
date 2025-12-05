from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt
from styles import apply_global_style


class HomePage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        title = QLabel("AI 투자성향 진단")
        title.setObjectName("title")

        subtitle = QLabel("한국인의 건전한 장기투자를 위한 금융 AI 플랫폼")
        subtitle.setObjectName("subtitle")

        start_btn = QPushButton("시작하기 →")
        start_btn.setFixedWidth(200)
        start_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)
        apply_global_style(self)
