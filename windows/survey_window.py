from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QFrame,
    QGraphicsOpacityEffect, QMessageBox
)

from styles import apply_global_style
scores = {
    1: {1: 12.5, 2: 12.5, 3: 9.3, 4: 6.2, 5: 3.1},
    2: {1: 3.1,  2: 6.2,  3: 9.3, 4: 12.5, 5: 15.6},
    3: {1: 3.1,  2: 6.2,  3: 9.3, 4: 12.5, 5: 15.6},
    4: {1: 3.1,  2: 6.2,  3: 9.3, 4: 12.5, 5: None},   # ⑤ 없음
    5: {1: 15.6, 2: 12.5, 3: 9.3, 4: 6.2, 5: 3.1},
    6: {1: 9.3,  2: 6.2,  3: 3.1, 4: None, 5: None},   # ④,⑤ 없음
    7: {1: -6.2, 2: 6.2,  3: 12.5, 4: 18.7, 5: None}   # ⑤ 없음
}
risk_profiles = {
    "안정형": "예금이나 적금 수준의 수익률을 기대하며, 투자원금에 손실이 발생하는 것을 원하지 않는다. "
           "원금 손실의 우려가 없는 상품에 투자하는 데 바람직하다.",
    "안정추구형": "투자원금의 손실 위험은 최소화하고, 이자·배당 등 안정적인 수익을 목표로 한다. "
             "다만 수익을 위해 단기적인 손실을 수용할 수 있으며 일부를 변동성 높은 상품에도 투자할 수 있다. "
             "채권형 금융상품이 적당하다.",
    "위험중립형": "투자에는 그에 따른 위험이 있다는 것을 인식하고 있으며, 예·적금보다 높은 수익을 기대한다면 "
             "일정 수준의 손실 위험을 감수할 수 있다. 적립식펀드나 주식연동형 등 중위험·중수익 펀드가 적당하다.",
    "적극투자형": "원금 보전보다 높은 수준의 수익을 추구하는 편이다. 투자자금의 상당 부분을 주식, 주식형 펀드, "
             "파생상품 등 위험자산에 투자할 의향이 있다. 해외·국내 주식형펀드나 비보장형 ELS도 고려할 수 있다.",
    "공격투자형": "시장평균수익률보다 크게 높은 수익을 목표로 하며, 큰 손실 위험도 적극 수용한다. "
             "투자자금 대부분을 주식, 주식형 펀드, 파생상품 등 고위험 자산에 투자할 의향이 있다. "
             "주식 비중 70% 이상 펀드가 적당하다."
}


def classify_risk(total_score: float) -> str:
    if total_score <= 20:
        return "안정형"
    elif total_score <= 40:
        return "안정추구형"
    elif total_score <= 60:
        return "위험중립형"
    elif total_score <= 80:
        return "적극투자형"
    else:
        return "공격투자형"


def evaluate_investor(answers: dict) -> dict:
    total = 0.0

    for q_num, choice in answers.items():
        point = scores[q_num].get(choice)
        if point is None:
            raise ValueError(f"{q_num}번 문항의 '{choice}'번 보기는 점수표에 존재하지 않습니다.")
        total += point

    risk_type = classify_risk(total)
    description = risk_profiles[risk_type]

    return {
        "총점": total,
        "투자성향": risk_type,
        "설명": description
    }


class SurveyPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack              # QStackedWidget 같은 거 들어옴
        self.current_index = 0          # 현재 질문 인덱스 (0 ~ 6)
        self.answers: dict[int, int] = {}   # {문항번호: 보기번호}
        self.last_result: dict | None = None
        self.questions = [
            {
                "id": 1,
                "title": "1. 우선, 당신의 나이를 알려주세요.",
                "subtitle": "투자를 이야기할 때, 나이도 중요한 기준이 되거든요.",
                "options": [
                    "19세 이하",
                    "20~40세",
                    "41~50세",
                    "51~60세",
                    "61세 이상",
                ],
            },
            {
                "id": 2,
                "title": "2. 내 돈을 얼마나 오래 투자해둘 수 있을까요?",
                "subtitle": "“언제 써야 하는 돈인지”에 따라 투자 방식도 달라집니다.",
                "options": [
                    "6개월 안에는 써야 해요",
                    "약 6개월~1년 정도는 괜찮아요",
                    "1년~2년 정도는 괜찮아요",
                    "2년~3년 정도는 괜찮아요",
                    "3년 이상은 묵혀둘 수 있어요",
                ],
            },
            {
                "id": 3,
                "title": "3. 지금까지 경험해본 투자 방식은 어떤 것들이 있나요?",
                "subtitle": "어렵게 생각하지 마세요. “이 정도는 해봤다” 싶은 걸 골라주세요.",
                "options": [
                    "예‧적금, 국채/지방채, MMF, CMA 같은 아주 안정적인 것만 해봤다",
                    "안정적인 채권이나 원금 보존형 상품(ELS 등) 정도는 해봤다",
                    "일부 위험이 있는 펀드나 원금이 전부 보장되지 않는 상품도 해봤다",
                    "주식이나 변동성이 있는 펀드 등, 수익·손실이 크게 움직일 수 있는 것도 해봤다",
                    "선물/옵션, 레버리지·파생상품 등 고위험 상품까지 경험해봤다",
                ],
            },
            {
                "id": 4,
                "title": "4. 금융상품에 대해 얼마나 알고 있다고 느끼시나요?",
                "subtitle": "“내가 어느 정도 아는지” 편하게 느낌만 골라주세요.",
                "options": [
                    "거의 몰라요. 투자 판단을 스스로 해본 적이 없어요",
                    "주식과 채권의 차이 정도는 알아요",
                    "주요 금융상품들의 특징은 어느 정도 구분할 수 있어요",
                    "웬만한 투자상품의 구조와 차이는 대부분 이해하고 있어요",
                ],
            },
            {
                "id": 5,
                "title": "5. 지금 투자하려는 돈이 내 전체 금융자산에서 차지하는 비중은 어느 정도인가요?",
                "subtitle": "“이 돈이 내 전체 자산에서 얼마나 중요한 돈인지” 알려주는 질문이에요.",
                "options": [
                    "10% 이하",
                    "10~20%",
                    "20~30%",
                    "30~40%",
                    "40% 이상",
                ],
            },
            {
                "id": 6,
                "title": "6. 당신의 현재 수입 상황은 어떤 편인가요?",
                "subtitle": "수입이 안정적인지에 따라 감당할 수 있는 투자 위험도 달라집니다.",
                "options": [
                    "지금 꾸준한 수입이 있고 앞으로도 비슷하거나 좋아질 것 같아요",
                    "지금은 수입이 있지만 앞으로 줄어들거나 불안정해질 수도 있어요",
                    "지금은 일정한 수입이 없고, 연금이나 비슷한 소득이 주 수입원이에요",
                ],
            },
            {
                "id": 7,
                "title": "7. 만약 투자에서 손실이 난다면… 어느 정도까지 감당할 수 있을까요?",
                "subtitle": "사람마다 다르니 어떤 선택이든 괜찮아요.",
                "options": [
                    "손실이 나는 건 절대 안 돼요. 원금 보장이 가장 중요해요",
                    "10% 정도까지는 손실을 받아들일 수 있어요",
                    "20% 정도까지는 감수할 수 있을 것 같아요",
                    "더 높은 수익을 노릴 수 있다면 위험도 어느 정도 괜찮아요",
                ],
            },
        ]

        self._build_ui()
        apply_global_style(self)
        self._load_question()
    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(16)

        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        main_layout.addWidget(self.progress_label)

        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("story")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addSpacing(10)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setMinimumWidth(900)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setSpacing(12)

        self.option_buttons: list[QPushButton] = []
        for i in range(5):
            btn = QPushButton("")
            btn.setFixedHeight(60)
            btn.clicked.connect(lambda checked, idx=i: self._on_option_clicked(idx))
            self.option_buttons.append(btn)
            self.card_layout.addWidget(btn)

        main_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        main_layout.addStretch()

    def _load_question(self):
        q = self.questions[self.current_index]

        self.progress_label.setText(f"{self.current_index + 1} / {len(self.questions)}")

        self.title_label.setText(q["title"])
        self.subtitle_label.setText(q["subtitle"])

        options = q["options"]

        for i, btn in enumerate(self.option_buttons):
            if i < len(options):
                btn.show()
                btn.setText(options[i])
            else:
                btn.hide()

        self._fade_in(self.card)

    def _on_option_clicked(self, idx: int):
        q = self.questions[self.current_index]
        qid = q["id"]

        self.answers[qid] = idx + 1
        self._go_next_or_finish()

    def _go_next_or_finish(self):
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self._load_question()
        else:
            self._finish_survey()

    def _finish_survey(self):
        # 모든 문항이 답변되었는지 확인
        missing = [
            q["id"] for q in self.questions
            if q["id"] not in self.answers
        ]
        if missing:
            QMessageBox.warning(
                self,
                "안내",
                f"아직 답하지 않은 문항이 있습니다: {missing}"
            )
            return

        try:
            result = evaluate_investor(self.answers)
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                f"점수 계산 중 오류가 발생했습니다.\n\n{e}"
            )
            return

        self.last_result = result

        result_page = self.stack.widget(3)
        if hasattr(result_page, "set_result"):
            result_page.set_result(result)
        self.stack.setCurrentIndex(3)

    def _fade_in(self, widget):
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.start()
