PRIMARY_COLOR = "#1A2A4F"   # 네이비
ACCENT_COLOR  = "#4C7FFF"   # 파란색 포인트
BG_COLOR      = "#F5F7FA"   # 연한 배경색

def apply_global_style(widget):
    widget.setStyleSheet(f"""
        QWidget {{
            background-color: {BG_COLOR};
            font-family: 'Malgun Gothic';
        }}
        QPushButton {{
            background-color: {ACCENT_COLOR};
            border-radius: 8px;
            padding: 12px;
            color: white;
            font-size: 16px;
        }}
        QPushButton:hover {{
            background-color: #3B6FE0;
        }}
        QLabel#title {{
            font-size: 28px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
        }}
        QLabel#subtitle {{
            font-size: 16px;
            color: #555;
        }}
        QFrame#card {{
            background-color: white;
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #E5E7EB;
        }}
    """)
