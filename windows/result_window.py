# windows/result_window.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFrame
from styles import apply_global_style


class ResultPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.risk_profile = "공격형"  # 기본값(예시). 설문에서 나중에 업데이트.

        title = QLabel("진단 결과")
        title.setObjectName("title")

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout()

        self.result_label = QLabel("당신의 투자성향: ⚡ 적극투자형(예시)")
        self.result_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.msg = QLabel(
            "📌 장기투자 코칭 메시지(예시)\n\n"
            "- 위험 감내 수준이 높습니다.\n"
            "- 성장형 ETF 비중이 적합합니다.\n"
            "- 단기매매를 줄이면 수익률 안정성이 높아집니다."
        )
        self.msg.setStyleSheet("font-size: 14px; color: #444;")

        card_layout.addWidget(self.result_label)
        card_layout.addWidget(self.msg)
        card.setLayout(card_layout)

        back_btn = QPushButton("← 처음으로")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        # 새로 추가: 백테스트 버튼
        backtest_btn = QPushButton("📈 이 성향으로 백테스트 해보기")
        backtest_btn.clicked.connect(self.go_to_backtest)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(card)
        layout.addStretch()
        layout.addWidget(backtest_btn)  # <- 여기에 추가
        layout.addWidget(back_btn)

        self.setLayout(layout)
        apply_global_style(self)

    def go_to_backtest(self):
        """
        AppWindow.backtest_page에 성향 넘기고, 3번 페이지로 전환
        """
        # AppWindow에서 self.backtest_page를 만들어뒀기 때문에 이렇게 접근 가능
        self.stack.backtest_page.set_profile_from_result(self.risk_profile)
        self.stack.setCurrentIndex(3)

    # 설문 페이지에서 결과를 넘겨주고 싶을 때 사용할 메서드 (SurveyPage -> ResultPage)
    def set_result(self, risk_profile: str, coaching_text: str):
        self.risk_profile = risk_profile
        self.result_label.setText(f"당신의 투자성향: {risk_profile}")
        self.msg.setText(coaching_text)
