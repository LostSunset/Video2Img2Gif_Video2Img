#!/usr/bin/env python3
"""
PySide6 UI 離屏渲染截圖工具
用法: python _ui_preview.py [模組路徑] [類別名稱] [寬度] [高度]
範例: python _ui_preview.py src.main_window MainWindow 1280 720
"""

import sys
import os
import importlib

# 設置 offscreen 平台（必須在 QApplication 之前）
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer


def capture_ui(module_path: str, class_name: str, width: int = 1280, height: int = 720):
    app = QApplication(sys.argv)

    # 動態導入模組和類別
    module = importlib.import_module(module_path)
    WindowClass = getattr(module, class_name)

    # 創建並顯示視窗
    window = WindowClass()
    window.resize(width, height)
    window.show()

    # 確保完全渲染後截圖
    def do_capture():
        app.processEvents()
        pixmap = window.grab()
        output_path = "ui_preview.png"
        pixmap.save(output_path)
        print(f"UI 截圖已保存至: {output_path}")
        app.quit()

    # 延遲執行確保渲染完成
    QTimer.singleShot(200, do_capture)
    app.exec()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python _ui_preview.py <模組路徑> <類別名稱> [寬度] [高度]")
        print("範例: python _ui_preview.py src.main_window MainWindow 1280 720")
        sys.exit(1)

    module_path = sys.argv[1]
    class_name = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 720

    capture_ui(module_path, class_name, width, height)
