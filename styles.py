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
            border-radius: 10px;
            padding: 14px 26px;
            color: white;
            font-size: 18px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #3B6FE0;
        }}

        QLabel#title {{
            font-size: 32px;
            font-weight: 800;
            color: {PRIMARY_COLOR};
        }}
        QLabel#subtitle {{
            font-size: 18px;
            color: #555;
        }}
        QLabel#story {{
            font-size: 18px;
            color: #111;
            line-height: 150%;
            background-color: transparent;   

        }}

        QFrame#card {{
            background-color: white;
            border-radius: 18px;
            padding: 32px 40px;
            border: 1px solid #E5E7EB;
        }}
    """)
