from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QFrame, QGraphicsOpacityEffect
)
from styles import apply_global_style


class SurveyPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        # ------------------------------
        # 실제 테스트 질문 데이터
        # ------------------------------
        self.questions = [
            {
                "title": "“누가 내 마음을 들여다봤나?“",
                "subtitle": "SNS 광고에서 본 신상, 완전히 내 취향이에요.\n내 마음에 가장 먼저 떠오른 생각은...",
                "options": [
                    "사고 싶다. 근데 막상 사고 안 쓰면 어떡하지?",
                    "고민은 배송을 늦출 뿐. 지금 결제해야지!",
                    "할인 안 하나? 온라인 검색해 봐야겠다",
                    "관련 주식 좀 찾아봐야겠는데?"
                ]
            },
            {
                "title": "“축하합니다. 복권 3등에 당첨되셨어요!“",
                "subtitle": "3등 당첨금은 150만 원이에요.\n완전히 내 마음대로 사용 가능한 돈이죠.",
                "options": [
                    "일단 예적금 통장에 넣어둬야지",
                    "역시 난 럭키! 여행부터 가야지",
                    "100만 원은 대출 갚고 나머진 저축",
                    "공돈이니까 레버리지 상품에 투자!"
                ]
            },
            {
                "title": "“갑자기 큰돈 나갈 일이 이렇게 많이?!“",
                "subtitle": "이번 달 경조사만 네 번에,\n노트북과 냉장고 고장까지 겹쳤어요. 나는...",
                "options": [
                    "나에게 왜 이런 시련이... 통장 잔고 체크!",
                    "돈 쓸 핑계? 오히려 좋아. 한 번 살 때 제대로!",
                    "꼭 필요한 지출만 하고 중고/렌탈을 찾는다",
                    "어차피 나갈 돈, 필요한 거면 바로 산다!"
                ]
            },
            {
                "title": "“지금 집을 사는 게 어때요?”",
                "subtitle": "대출은 부담되지만 전월세나 매매나 비슷한 상황.\n나는...",
                "options": [
                    "대출 부담이 싫어 월세부터 알아본다",
                    "직접 매물을 봐야 결정할 수 있을 것 같다",
                    "커리어·가계부 점검 → 매물 입지를 분석한다",
                    "투자 개념으로 보면 매매가 낫다"
                ]
            },
            {
                "title": "“이게 얼마 만이야!“",
                "subtitle": "오랜만의 친구와 만남.\n결제 순간 나는...",
                "options": [
                    "정산하게 얼마 나왔는지 알려줘!",
                    "오랜만이니까 내가 낼게!",
                    "깔끔하게 더치페이 하자!",
                    "내가 먼저 결제할게. 실적 챙겨야지!"
                ]
            },
        ]

        self.current_index = 0

        # ------------------------------
        # 상단 진행률 라벨
        # ------------------------------
        self.progress = QLabel("1 / 5")
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress.setStyleSheet("font-size: 14px; font-weight: bold;")

        # ------------------------------
        # 질문 타이틀 / 서브타이틀
        # ------------------------------
        self.title_label = QLabel()
        self.title_label.setObjectName("story")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("story")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)

        # ------------------------------
        # 카드 스타일 컨테이너
        # ------------------------------
        self.card = QFrame()
        self.card.setObjectName("card")

        self.card_layout = QVBoxLayout()
        self.card_layout.setSpacing(12)

        self.option_buttons = []
        for _ in range(4):
            btn = QPushButton("")
            btn.setFixedHeight(60)
            btn.clicked.connect(self._on_option_selected)
            self.option_buttons.append(btn)
            self.card_layout.addWidget(btn)

        self.card.setLayout(self.card_layout)

        # ------------------------------
        # 레이아웃 구성
        # ------------------------------
        layout = QVBoxLayout()
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addSpacing(20)
        layout.addWidget(self.card)
        layout.addStretch()

        self.setLayout(layout)
        apply_global_style(self)

        self._load_question()

    # ------------------------------
    # 현재 질문 세트를 UI에 로드
    # ------------------------------
    def _load_question(self):
        q = self.questions[self.current_index]

        self.progress.setText(f"{self.current_index+1} / {len(self.questions)}")
        self.title_label.setText(q["title"])
        self.subtitle_label.setText(q["subtitle"])

        for i, text in enumerate(q["options"]):
            self.option_buttons[i].setText(text)

        self._fade_in(self.card)

    # ------------------------------
    # 선택지 클릭 시 다음 질문으로 이동
    # ------------------------------
    def _on_option_selected(self):
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self._load_question()
        else:
            # 마지막 질문 응답 → 결과 페이지로 이동
            self.stack.setCurrentIndex(3)

    # ------------------------------
    # 부드러운 페이드인
    # ------------------------------
    def _fade_in(self, widget):
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.start()
