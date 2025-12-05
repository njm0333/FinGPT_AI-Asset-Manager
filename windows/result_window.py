from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QFrame,
    QGraphicsOpacityEffect, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer

from styles import apply_global_style

#done

class ResultPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.result = None
        self.animations = []

        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(900)
        card.setMinimumHeight(550)
        card.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.MinimumExpanding)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(24)
        card_layout.setContentsMargins(32, 32, 32, 32)

        self.widgets = []

        self.title_label = QLabel("나의 투자 성향 결과")
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        card_layout.addWidget(self.title_label)
        self.widgets.append(self.title_label)

        self.subtitle_label = QLabel("Fin GPT가 설문 결과를 바탕으로 당신의 투자 성향을 정리해봤어요.")
        self.subtitle_label.setObjectName("story")
        self.subtitle_label.setWordWrap(True)
        card_layout.addWidget(self.subtitle_label)
        self.widgets.append(self.subtitle_label)

        self.risk_label = QLabel("투자 성향: -")
        self.risk_label.setObjectName("story")
        card_layout.addWidget(self.risk_label)
        self.widgets.append(self.risk_label)

        self.score_label = QLabel("")
        self.score_label.setObjectName("story")
        card_layout.addWidget(self.score_label)
        self.widgets.append(self.score_label)

        self.desc_label = QLabel("")
        self.desc_label.setObjectName("story")
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        card_layout.addWidget(self.desc_label)
        self.widgets.append(self.desc_label)

        self.coaching_label = QLabel("")
        self.coaching_label.setObjectName("story")
        self.coaching_label.setWordWrap(True)
        card_layout.addWidget(self.coaching_label)
        self.widgets.append(self.coaching_label)

        self.next_button = QPushButton("투자 성향에 맞춘 포트폴리오 상담 받기")
        self.next_button.setFixedWidth(420)
        self.next_button.clicked.connect(self._go_next)
        self.widgets.append(self.next_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 40, 32, 40)
        layout.setSpacing(32)

        layout.addStretch(1)
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(24)
        layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)

        self.setLayout(layout)
        apply_global_style(self)

        for w in self.widgets:
            eff = QGraphicsOpacityEffect()
            eff.setOpacity(0)
            w.setGraphicsEffect(eff)

        QTimer.singleShot(0, self._start_fadein)

    def set_result(self, result: dict):
        self.result = result

        self.risk_label.setText(f"투자 성향: {result.get('투자성향', '-')}")
        self.score_label.setText(f"총점: {result.get('총점', 0.0):.1f}점")
        self.desc_label.setText(result.get("설명", ""))
        self.coaching_label.setText(
            self._build_coaching_text(result.get("투자성향", ""))
        )

        self._reset_fadein()

    def _build_coaching_text(self, risk_type: str) -> str:
        coaching_map = {
            "안정형": (
                "● 원금 보존이 가장 중요하신 타입이에요.\n"
                "· 예·적금, 국공채, MMF처럼 변동성이 낮은 상품 위주로 포트폴리오를 구성하는 게 좋습니다.\n"
                "· 인플레이션을 감안해, 너무 낮은 금리 상품만 고집하지 않도록 주기적으로 점검해 보세요."
            ),
            "안정추구형": (
                "● 수익도 원하지만, 큰 손실은 피하고 싶은 타입이에요.\n"
                "· 채권/채권형 펀드 + 일부 주식·ETF를 섞은 구조가 잘 맞습니다.\n"
                "· 시장이 흔들릴 때도 계획한 비중을 유지하는 것이 중요합니다."
            ),
            "위험중립형": (
                "● 수익과 위험을 균형 있게 바라보는 타입이에요.\n"
                "· 적립식 펀드, 분산된 ETF 포트폴리오가 잘 맞습니다.\n"
                "· 단기 수익에 흔들리기보다는 3년 이상을 보는 장기 계획을 세워보세요."
            ),
            "적극투자형": (
                "● 수익을 위해 어느 정도 변동성을 감수할 수 있는 타입이에요.\n"
                "· 성장주·섹터 ETF 비중을 높이되, 채권/현금성 자산으로 안전판을 일부 두는 게 좋습니다.\n"
                "· 손절·리밸런싱 기준을 미리 정해 두면 감정적인 매매를 줄일 수 있습니다."
            ),
            "공격투자형": (
                "● 높은 수익을 위해 큰 변동성도 감내하는 타입이에요.\n"
                "· 주식·주식형 펀드·테마 ETF 비중이 높을 수 있지만, 전체 자산 중 투자 가능한 범위를 넘지 않도록 주의하세요.\n"
                "· 레버리지/파생상품 사용 시에는 투자 금액 한도를 꼭 정해 두는 것을 추천합니다."
            ),
        }

        return coaching_map.get(
            risk_type,
            "설문 결과를 바탕으로 Fin GPT가 앞으로의 투자 여정을 함께 도와드릴게요."
        )

    def _go_next(self):
        try:
            self.stack.setCurrentIndex(4)
        except:
            pass
    def _start_fadein(self):
        for i, w in enumerate(self.widgets):
            QTimer.singleShot(i * 50, lambda w=w: self._fade(w))

    def _reset_fadein(self):
        for w in self.widgets:
            eff = w.graphicsEffect()
            eff.setOpacity(0)
        self.animations.clear()
        self._start_fadein()

    def _fade(self, widget):
        eff = widget.graphicsEffect()
        anim = QPropertyAnimation(eff, b"opacity", self)
        anim.setDuration(500)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self.animations.append(anim)
