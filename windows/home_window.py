from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from styles import apply_global_style


class HomePage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        # --- 위젯 구성 ---
        self.title = QLabel("Fin GPT")
        self.title.setObjectName("title")

        self.subtitle = QLabel("한국인의 건전한 장기투자를 위한 금융 AI 플랫폼")
        self.subtitle.setObjectName("subtitle")

        self.start_btn = QPushButton("시작하기")
        self.start_btn.setFixedWidth(200)
        self.start_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

        apply_global_style(self)
        self._apply_fadein_effects()

    def _apply_fadein_effects(self):
        widgets = [self.title, self.subtitle, self.start_btn]
        base_delay = 0

        for i, w in enumerate(widgets):
            delay = base_delay + i * 250  # 순차 지연(ms 단위)

            def animate_widget(widget=w):
                opacity = QGraphicsOpacityEffect()
                widget.setGraphicsEffect(opacity)
                anim = QPropertyAnimation(opacity, b"opacity", self)
                anim.setDuration(1000)
                anim.setStartValue(0)
                anim.setEndValue(1)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                anim.start()

                pos_anim = QPropertyAnimation(widget, b"pos", self)
                start_pos = widget.pos() - QPoint(0, 20)
                pos_anim.setStartValue(start_pos)
                pos_anim.setEndValue(widget.pos())
                pos_anim.setDuration(1000)
                pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                pos_anim.start()

            QTimer.singleShot(delay, animate_widget)
