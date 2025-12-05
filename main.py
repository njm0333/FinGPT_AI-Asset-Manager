from PyQt6.QtWidgets import QApplication
from windows.app_window import AppWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AppWindow()
    win.resize(550, 700)
    win.show()
    sys.exit(app.exec())
