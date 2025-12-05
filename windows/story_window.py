from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QGraphicsOpacityEffect, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from styles import apply_global_style


class StoryPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        # ---- 스토리 텍스트 ----
        story_texts = [
            "최근 들어 주식이 올랐다, 경제가 불안하다…\n이런 말들이 참 많이 들려오죠.",
            "하지만 막상 투자라고 하면\n어디서부터 시작해야 할지 막막한 당신.",
            "돈을 굴린다기보다\n돈에게 끌려다니는 기분이 들 때도 있었을 거예요.",
            "누군가는 말합니다.\n“장기 투자가 중요하다”고.\n하지만 무엇을, 왜 장기 투자해야 하는지는\n아무도 자세히 알려주지 않죠.",
            "그래서 준비했습니다.\n당신이 어렵지 않게 도와줄 금융 가이드.",
            "지금보다 더 안정적인 내일을 위해,\n건전한 장기 투자의 첫걸음을\nFin GPT가 함께 합니다."
        ]

        # ---- 카드 위젯 ----
        card = QFrame()
        card.setObjectName("card")

        card_layout = QVBoxLayout()
        card_layout.setSpacing(24)

        self.widgets = []

        for text in story_texts:
            lbl = QLabel(text)
            lbl.setObjectName("story")
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            card_layout.addWidget(lbl)
            self.widgets.append(lbl)

        # 마지막 버튼
        self.start_btn = QPushButton("투자성향 알아보기")
        self.start_btn.setFixedWidth(200)
        self.start_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        card_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.widgets.append(self.start_btn)

        card.setLayout(card_layout)

        # 전체 레이아웃
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

        apply_global_style(self)

        # 처음에 투명하게 만들기
        for w in self.widgets:
            eff = QGraphicsOpacityEffect()
            eff.setOpacity(0)
            w.setGraphicsEffect(eff)

        # fade-in 실행
        QTimer.singleShot(0, self._start_fadein)

    # ------------------------------
    # SurveyPage 스타일의 순수 Fade-in
    # ------------------------------
    def _start_fadein(self):
        for i, w in enumerate(self.widgets):
            QTimer.singleShot(i * 300, lambda w=w: self._fade_in(w))

    def _fade_in(self, widget):
        eff = widget.graphicsEffect()
        anim = QPropertyAnimation(eff, b"opacity", self)
        anim.setDuration(700)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
