
#done

PRIMARY_COLOR = "#1A2A4F"   # 네이비
ACCENT_COLOR  = "#4C7FFF"   # 파란색 포인트
BG_COLOR      = "#F5F7FA"   # 연한 배경색
TEXT_COLOR    = "#111111"   # 기본 본문 색
SUBTEXT_COLOR = "#555555"   # 서브텍스트 색

def apply_global_style(widget):
    widget.setStyleSheet(f"""
        /* 전체 기본 설정 */
        QWidget {{
            background-color: {BG_COLOR};
            font-family: 'Malgun Gothic';
            color: {TEXT_COLOR};
        }}

        /* 버튼 */
        QPushButton {{
            background-color: {ACCENT_COLOR};
            border-radius: 10px;
            padding: 12px 24px;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #3B6FE0;
        }}
        QPushButton:disabled {{
            background-color: #C4D1FF;
            color: #F5F7FA;
        }}

        /* 타이틀/서브타이틀/스토리 텍스트 */
        QLabel#title {{
            font-size: 32px;
            font-weight: 800;
            color: {PRIMARY_COLOR};
        }}
        QLabel#subtitle {{
            font-size: 18px;
            color: {SUBTEXT_COLOR};
        }}
        QLabel#story {{
            font-size: 16px;
            color: {TEXT_COLOR};
            line-height: 150%;
            background-color: transparent;
        }}

        /* 카드 */
        QFrame#card {{
            background-color: white;
            border-radius: 18px;
            padding: 32px 40px;
            border: 1px solid #E5E7EB;
        }}

        /* 입력창 / 텍스트창 / 테이블 */
        QLineEdit,
        QComboBox,
        QDateEdit,
        QPlainTextEdit,
        QTableView,
        QTableWidget {{
            background-color: #F9FAFB;
            color: {TEXT_COLOR};
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 6px 8px;
            selection-background-color: {ACCENT_COLOR};
            selection-color: white;
        }}

        QPlainTextEdit {{
            background-color: white;
        }}

        /* 콤보박스의 드롭다운 리스트 */
        QComboBox QAbstractItemView {{
            background-color: white;
            color: {TEXT_COLOR};
            selection-background-color: {ACCENT_COLOR};
            selection-color: white;
        }}

        /* 탭 위쪽 바/내용 영역 */
        QTabWidget::pane {{
            border: none;
        }}
        QTabBar::tab {{
            background-color: transparent;
            padding: 8px 18px;
            margin-right: 2px;
            color: #777777;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            color: {PRIMARY_COLOR};
            border-bottom: 2px solid {ACCENT_COLOR};
        }}
    """)
