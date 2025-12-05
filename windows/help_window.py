
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy, QScrollArea, QHBoxLayout
)
from PyQt6.QtCore import Qt
from styles import apply_global_style


class HelpPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(24)

        header_title = QLabel("PCA가 어려운 분들을 위한 이해 도우미")
        header_title.setObjectName("title")
        root.addWidget(header_title)

        header_sub = QLabel(
            "티커부터 포트폴리오, PCA, 요인, 쏠림, 리밸런싱까지\n"
            "Fin GPT가 한 번에 천천히 정리해 드릴게요."
        )
        header_sub.setObjectName("subtitle")
        header_sub.setWordWrap(True)
        root.addWidget(header_sub)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(24)
        root.addLayout(main_layout, stretch=1)

        card = QFrame()
        card.setObjectName("card")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        def add_section(title, body):
            t = QLabel(title)
            t.setObjectName("subtitle")

            b = QLabel(body)
            b.setObjectName("story")
            b.setWordWrap(True)

            content_layout.addWidget(t)
            content_layout.addWidget(b)

        add_section(
            "❓ 1. 티커가 뭔가요?",
            "주식마다 붙어 있는 고유한 이름표라고 생각하면 돼요.\n\n"
            "애플 = AAPL\n"
            "삼성전자 = 005930.KS\n"
            "테슬라 = TSLA\n\n"
            "“이 종목을 사겠다”라고 할 때 우리는 회사 이름이 아니라 이 "
            "티커(symbol)을 사용합니다.\n\n"
            "마치 사람의 주민번호처럼, 전 세계 어디에서든 정확히 같은 회사를 "
            "가리킬 수 있는 공식 코드예요."
        )

        add_section(
            "❓ 2. 포트폴리오가 뭔가요?",
            "여러분이 가진 투자 자산의 바구니입니다.\n\n"
            "예를 들어,\n\n"
            "애플 30%\n"
            "테슬라 20%\n"
            "ETF 50%\n\n"
            "이렇게 구성돼 있다면 이것이 바로 당신의 포트폴리오예요.\n"
            "과자를 사듯이 초콜릿 3개, 젤리 2개, 사탕 5개 사면 "
            "그게 \"과자 포트폴리오\"인 것처럼요.\n\n"
            "포트폴리오는 “나는 어떤 성향의 자산에, 얼마나 투자하고 있는가?”를 "
            "보여주는 지도입니다."
        )

        add_section(
            "❓ 3. PCA 분석이란?",
            "투자로 고민하는 분들이 가장 어려워하는 단어가 바로 이 PCA!!\n"
            "이걸 아주 간단하게 설명해볼게요.\n\n"
            "우리가 가지고 있는 주식들을 가만히 들여다보면, "
            "비슷하게 움직이는 친구들끼리 몰려다니는 것처럼 보일 때가 있어요.\n\n"
            "· 기술주끼리 같이 오르락내리락하고,\n"
            "· 경기 민감주는 묶여서 움직이고,\n"
            "· 배당·필수소비재 같은 안정적인 친구들은 또 따로 움직이고요.\n\n"
            "이 비슷한 움직임의 무리(요인)를 자동으로 찾아주는 기술이 바로 PCA입니다.\n\n"
            "원 세 개가 있다고 해볼게요.\n\n"
            "원 1: 시장 전체 흐름을 따라가는 그룹\n"
            "원 2: 기술·성장 중심 그룹\n"
            "원 3: 안정적·방어형 그룹\n\n"
            "PCA는 이 원 안에 각 종목을 “이 종목은 어디 성향이 강하지?” 하고 "
            "자동으로 배치해 주는 친구예요."
        )

        add_section(
            "❓ 4. 요인이란?",
            "요인은 주식이 가진 ‘성격’이라고 생각하면 됩니다.\n\n"
            "예를 들어:\n\n"
            "🔹 Factor 1 — 시장 전체 영향\n"
            "   대부분의 종목이 함께 오르고, 함께 떨어질 때 만들어지는 흐름\n\n"
            "🔹 Factor 2 — 기술·성장 성향\n"
            "   혁신 기업, 기술주가 몰려 있는 그룹\n\n"
            "🔹 Factor 3 — 안정적·방어적 성향\n"
            "   경기와 관계없이 꾸준한 기업들 (배당·필수소비재·헬스케어 등)\n\n"
            "🔹 Factor 4 — 특정 업종 중심\n"
            "   반도체, 자동차, 에너지 등 특정 섹터의 성격이 강한 그룹\n\n"
            "요인은 이렇게 “주식들의 공통된 움직임”을 설명해주는 중요한 힌트예요."
        )

        add_section(
            "❓ 5. 요인 노출도란?",
            "어떤 요인에 내 포트폴리오가 얼마나 영향을 받는지를 나타내는 비율이에요.\n\n"
            "예를 들어:\n\n"
            "기술 요인에 40%\n"
            "시장 전체 요인에 30%\n"
            "안정적 요인에 20%\n\n"
            "이렇게 나오면,\n"
            "“아, 나는 기술주 성향이 좀 강하구나” 하고 이해할 수 있죠.\n\n"
            "즉, 내 자산이 어떤 성격을 띠고 돌아가고 있는지 보여주는 지표입니다."
        )

        add_section(
            "❓ 6. 쏠림이란?",
            "포트폴리오가 특정 성향에 과하게 몰려 있는 상태예요.\n\n"
            "예)\n"
            "· 기술주에 너무 편중\n"
            "· 특정 업종에 너무 집중\n"
            "· 안전 자산이 거의 없음\n\n"
            "이렇게 되면 어떤 사건이 발생했을 때 계좌가 크게 흔들릴 위험이 생겨요.\n"
            "그래서 “쏠림”을 진단하는 게 중요합니다."
        )

        add_section(
            "❓ 7. 리밸런싱이란?",
            "한쪽으로 기울어진 포트폴리오를 다시 균형 잡히게 만드는 과정이에요.\n\n"
            "· 너무 많은 요인 → 조금 줄이고\n"
            "· 너무 적은 요인 → 조금 늘리고\n\n"
            "목표 투자 성향에 맞게 조정하는 것입니다.\n\n"
            "과자를 10개 샀는데\n"
            "초콜릿 7개\n"
            "젤리 2개\n"
            "사탕 1개\n"
            "이렇게 되어 있다면… 조금 불균형하죠?\n\n"
            "초콜릿을 조금 줄이고, 젤리나 사탕을 더 사면 균형이 잡히는 것처럼,\n"
            "포트폴리오도 그렇게 균형을 맞춰주는 거예요."
        )

        add_section(
            "❓ 마무리",
            "투자는 ‘잘 아는 사람만 하는 어려운 것’처럼 느껴질 수 있어요.\n"
            "하지만 원리를 차근차근 이해하기만 해도 훨씬 안정적인 투자가 가능합니다.\n\n"
        )

        content_layout.addStretch(1)

        scroll.setWidget(content_widget)
        card_layout.addWidget(scroll)
        main_layout.addWidget(card, stretch=1)

        btn_back = QPushButton("돌아가기")
        btn_back.setMinimumHeight(44)
        btn_back.setFixedWidth(260)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(4))

        root.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        apply_global_style(self)
