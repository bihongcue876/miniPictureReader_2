#!/usr/bin/env python3
"""PictureReader - 轻量级跨平台图片查看与管理工具."""

import sys
from PySide6.QtWidgets import QApplication
from ui.app import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PictureReader")
    app.setOrganizationName("PictureReader")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
