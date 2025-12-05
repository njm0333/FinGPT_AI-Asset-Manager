from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFrame
from styles import apply_global_style


class ResultPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        title = QLabel("진단 결과")
        title.setObjectName("title")

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout()

        result = QLabel("당신의 투자성향: ⚡ 적극투자형(예시)")
        result.setStyleSheet("font-size: 18px; font-weight: bold;")

        msg = QLabel("📌 장기투자 코칭 메시지(예시)\n\n"
                     "- 위험 감내 수준이 높습니다.\n"
                     "- 성장형 ETF 비중이 적합합니다.\n"
                     "- 단기매매를 줄이면 수익률 안정성이 높아집니다.")
        msg.setStyleSheet("font-size: 14px; color: #444;")

        card_layout.addWidget(result)
        card_layout.addWidget(msg)
        card.setLayout(card_layout)

        back_btn = QPushButton("← 처음으로")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(card)
        layout.addStretch()
        layout.addWidget(back_btn)

        self.setLayout(layout)
        apply_global_style(self)
