from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt

from styles import apply_global_style


class ExplainPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.setObjectName("ExplainPage")

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(24)

        title = QLabel("보고서 분석")
        title.setObjectName("title")
        root.addWidget(title)

        subtitle = QLabel("Fin GPT가 분석한 PCA 리포트에요.")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        scroll_layout = QVBoxLayout(content)
        scroll_layout.setSpacing(20)

        self.explain_label = QLabel("")
        self.explain_label.setWordWrap(True)
        self.explain_label.setObjectName("story")
        self.explain_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_layout.addWidget(self.explain_label)
        scroll.setWidget(content)

        root.addWidget(scroll, stretch=1)

        back_btn = QPushButton("PCA 분석 화면으로 돌아가기")
        back_btn.setMinimumHeight(44)
        back_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        back_btn.clicked.connect(self._go_back)
        root.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignRight)

        apply_global_style(self)

    def set_explanation_text(self, text: str):
        self.explain_label.setText(text)

    def _go_back(self):
        self.stack.setCurrentIndex(4)
