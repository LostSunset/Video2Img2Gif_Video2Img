"""
Video2Img 主視窗 UI
"""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .converter import VideoConverter


class WorkerThread(QThread):
    """背景工作執行緒"""

    progress = Signal(int, int)  # current, total
    finished = Signal(str)  # result message
    error = Signal(str)  # error message

    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.task_func(*self.args, **self.kwargs)
            self.finished.emit(str(result))
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """主視窗"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video2Img - 影片與圖片轉換工具")
        self.setMinimumSize(800, 600)

        self.worker: WorkerThread | None = None
        self.selected_images: list[str] = []

        self._setup_ui()

    def _setup_ui(self):
        """設定 UI 元件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 標題
        title_label = QLabel("Video2Img")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("影片與圖片轉換工具")
        subtitle_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)

        # Tab 頁籤
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Tab 1: 影片轉圖片
        tab_widget.addTab(self._create_video_to_images_tab(), "影片 → 圖片")

        # Tab 2: 圖片轉 GIF/影片
        tab_widget.addTab(self._create_images_to_media_tab(), "圖片 → GIF/影片")

        # Tab 3: 影片轉 GIF
        tab_widget.addTab(self._create_video_to_gif_tab(), "影片 → GIF")

        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 狀態列
        self.status_label = QLabel("就緒")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 4px;")
        main_layout.addWidget(self.status_label)

    def _create_video_to_images_tab(self) -> QWidget:
        """建立影片轉圖片頁籤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # 輸入檔案
        input_group = QGroupBox("輸入影片")
        input_layout = QHBoxLayout(input_group)
        self.v2i_input_edit = QLineEdit()
        self.v2i_input_edit.setPlaceholderText("選擇影片檔案...")
        input_layout.addWidget(self.v2i_input_edit)
        browse_btn = QPushButton("瀏覽")
        browse_btn.clicked.connect(self._browse_video_for_images)
        input_layout.addWidget(browse_btn)
        layout.addWidget(input_group)

        # 輸出設定
        output_group = QGroupBox("輸出設定")
        output_layout = QVBoxLayout(output_group)

        # 輸出目錄
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("輸出目錄:"))
        self.v2i_output_dir_edit = QLineEdit()
        self.v2i_output_dir_edit.setPlaceholderText("選擇輸出目錄...")
        dir_layout.addWidget(self.v2i_output_dir_edit)
        dir_browse_btn = QPushButton("瀏覽")
        dir_browse_btn.clicked.connect(self._browse_output_dir_v2i)
        dir_layout.addWidget(dir_browse_btn)
        output_layout.addLayout(dir_layout)

        # 幀間隔
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("每幾幀輸出一張:"))
        self.v2i_interval_spin = QSpinBox()
        self.v2i_interval_spin.setRange(1, 1000)
        self.v2i_interval_spin.setValue(1)
        self.v2i_interval_spin.setToolTip("1 = 每幀都輸出")
        interval_layout.addWidget(self.v2i_interval_spin)
        interval_layout.addStretch()
        output_layout.addLayout(interval_layout)

        # 輸出格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("輸出格式:"))
        self.v2i_format_combo = QComboBox()
        self.v2i_format_combo.addItems(["png", "jpg", "bmp", "webp"])
        format_layout.addWidget(self.v2i_format_combo)
        format_layout.addStretch()
        output_layout.addLayout(format_layout)

        layout.addWidget(output_group)

        # 執行按鈕
        convert_btn = QPushButton("開始轉換")
        convert_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; "
            "font-size: 14px; padding: 10px; border-radius: 5px; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        convert_btn.clicked.connect(self._start_video_to_images)
        layout.addWidget(convert_btn)

        layout.addStretch()
        return widget

    def _create_images_to_media_tab(self) -> QWidget:
        """建立圖片轉 GIF/影片頁籤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # 圖片列表
        input_group = QGroupBox("輸入圖片")
        input_layout = QVBoxLayout(input_group)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("新增圖片")
        add_btn.clicked.connect(self._add_images)
        btn_layout.addWidget(add_btn)
        add_folder_btn = QPushButton("新增資料夾")
        add_folder_btn.clicked.connect(self._add_image_folder)
        btn_layout.addWidget(add_folder_btn)
        clear_btn = QPushButton("清除全部")
        clear_btn.clicked.connect(self._clear_images)
        btn_layout.addWidget(clear_btn)
        input_layout.addLayout(btn_layout)

        self.i2m_list_widget = QListWidget()
        self.i2m_list_widget.setMinimumHeight(150)
        input_layout.addWidget(self.i2m_list_widget)

        layout.addWidget(input_group)

        # 輸出設定
        output_group = QGroupBox("輸出設定")
        output_layout = QVBoxLayout(output_group)

        # 輸出檔案
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("輸出檔案:"))
        self.i2m_output_edit = QLineEdit()
        self.i2m_output_edit.setPlaceholderText("選擇輸出檔案...")
        file_layout.addWidget(self.i2m_output_edit)
        file_browse_btn = QPushButton("瀏覽")
        file_browse_btn.clicked.connect(self._browse_output_file_i2m)
        file_layout.addWidget(file_browse_btn)
        output_layout.addLayout(file_layout)

        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.i2m_fps_spin = QSpinBox()
        self.i2m_fps_spin.setRange(1, 120)
        self.i2m_fps_spin.setValue(10)
        fps_layout.addWidget(self.i2m_fps_spin)
        fps_layout.addStretch()
        output_layout.addLayout(fps_layout)

        # 輸出類型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("輸出類型:"))
        self.i2m_type_combo = QComboBox()
        self.i2m_type_combo.addItems(["GIF", "MP4", "AVI", "MOV", "WEBM"])
        type_layout.addWidget(self.i2m_type_combo)
        type_layout.addStretch()
        output_layout.addLayout(type_layout)

        layout.addWidget(output_group)

        # 執行按鈕
        convert_btn = QPushButton("開始轉換")
        convert_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; "
            "font-size: 14px; padding: 10px; border-radius: 5px; }"
            "QPushButton:hover { background-color: #229954; }"
        )
        convert_btn.clicked.connect(self._start_images_to_media)
        layout.addWidget(convert_btn)

        layout.addStretch()
        return widget

    def _create_video_to_gif_tab(self) -> QWidget:
        """建立影片轉 GIF 頁籤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # 輸入檔案
        input_group = QGroupBox("輸入影片")
        input_layout = QHBoxLayout(input_group)
        self.v2g_input_edit = QLineEdit()
        self.v2g_input_edit.setPlaceholderText("選擇影片檔案...")
        input_layout.addWidget(self.v2g_input_edit)
        browse_btn = QPushButton("瀏覽")
        browse_btn.clicked.connect(self._browse_video_for_gif)
        input_layout.addWidget(browse_btn)
        layout.addWidget(input_group)

        # 輸出設定
        output_group = QGroupBox("輸出設定")
        output_layout = QVBoxLayout(output_group)

        # 輸出檔案
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("輸出檔案:"))
        self.v2g_output_edit = QLineEdit()
        self.v2g_output_edit.setPlaceholderText("選擇輸出 GIF 檔案...")
        file_layout.addWidget(self.v2g_output_edit)
        file_browse_btn = QPushButton("瀏覽")
        file_browse_btn.clicked.connect(self._browse_output_file_v2g)
        file_layout.addWidget(file_browse_btn)
        output_layout.addLayout(file_layout)

        # 幀間隔
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("每幾幀取一幀:"))
        self.v2g_interval_spin = QSpinBox()
        self.v2g_interval_spin.setRange(1, 1000)
        self.v2g_interval_spin.setValue(1)
        self.v2g_interval_spin.setToolTip("1 = 每幀都取")
        interval_layout.addWidget(self.v2g_interval_spin)
        interval_layout.addStretch()
        output_layout.addLayout(interval_layout)

        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("GIF FPS:"))
        self.v2g_fps_spin = QSpinBox()
        self.v2g_fps_spin.setRange(1, 60)
        self.v2g_fps_spin.setValue(10)
        fps_layout.addWidget(self.v2g_fps_spin)
        fps_layout.addStretch()
        output_layout.addLayout(fps_layout)

        # 最大寬度
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("最大寬度 (0=不限制):"))
        self.v2g_max_width_spin = QSpinBox()
        self.v2g_max_width_spin.setRange(0, 4096)
        self.v2g_max_width_spin.setValue(0)
        self.v2g_max_width_spin.setToolTip("用於縮小 GIF 尺寸，0 表示不限制")
        width_layout.addWidget(self.v2g_max_width_spin)
        width_layout.addStretch()
        output_layout.addLayout(width_layout)

        layout.addWidget(output_group)

        # 執行按鈕
        convert_btn = QPushButton("開始轉換")
        convert_btn.setStyleSheet(
            "QPushButton { background-color: #9b59b6; color: white; "
            "font-size: 14px; padding: 10px; border-radius: 5px; }"
            "QPushButton:hover { background-color: #8e44ad; }"
        )
        convert_btn.clicked.connect(self._start_video_to_gif)
        layout.addWidget(convert_btn)

        layout.addStretch()
        return widget

    # === 瀏覽檔案方法 ===

    def _browse_video_for_images(self):
        """瀏覽影片檔案（影片轉圖片）"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇影片檔案",
            "",
            "影片檔案 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v *.mpeg *.mpg *.3gp);;所有檔案 (*.*)",
        )
        if file_path:
            self.v2i_input_edit.setText(file_path)
            # 自動設定輸出目錄
            if not self.v2i_output_dir_edit.text():
                output_dir = str(Path(file_path).parent / Path(file_path).stem)
                self.v2i_output_dir_edit.setText(output_dir)

    def _browse_output_dir_v2i(self):
        """瀏覽輸出目錄（影片轉圖片）"""
        dir_path = QFileDialog.getExistingDirectory(self, "選擇輸出目錄")
        if dir_path:
            self.v2i_output_dir_edit.setText(dir_path)

    def _add_images(self):
        """新增圖片"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "選擇圖片檔案",
            "",
            "圖片檔案 (*.png *.jpg *.jpeg *.bmp *.webp *.gif *.tiff *.tif);;所有檔案 (*.*)",
        )
        for path in file_paths:
            if path not in self.selected_images:
                self.selected_images.append(path)
                self.i2m_list_widget.addItem(QListWidgetItem(path))

    def _add_image_folder(self):
        """新增資料夾內的所有圖片"""
        dir_path = QFileDialog.getExistingDirectory(self, "選擇圖片資料夾")
        if dir_path:
            image_extensions = {
                ".png",
                ".jpg",
                ".jpeg",
                ".bmp",
                ".webp",
                ".gif",
                ".tiff",
                ".tif",
            }
            for file_name in sorted(os.listdir(dir_path)):
                if Path(file_name).suffix.lower() in image_extensions:
                    full_path = os.path.join(dir_path, file_name)
                    if full_path not in self.selected_images:
                        self.selected_images.append(full_path)
                        self.i2m_list_widget.addItem(QListWidgetItem(full_path))

    def _clear_images(self):
        """清除所有圖片"""
        self.selected_images.clear()
        self.i2m_list_widget.clear()

    def _browse_output_file_i2m(self):
        """瀏覽輸出檔案（圖片轉媒體）"""
        output_type = self.i2m_type_combo.currentText().lower()
        if output_type == "gif":
            filter_str = "GIF 檔案 (*.gif)"
        else:
            filter_str = f"影片檔案 (*.{output_type})"

        file_path, _ = QFileDialog.getSaveFileName(self, "選擇輸出檔案", "", filter_str)
        if file_path:
            self.i2m_output_edit.setText(file_path)

    def _browse_video_for_gif(self):
        """瀏覽影片檔案（影片轉 GIF）"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇影片檔案",
            "",
            "影片檔案 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v *.mpeg *.mpg *.3gp);;所有檔案 (*.*)",
        )
        if file_path:
            self.v2g_input_edit.setText(file_path)
            # 自動設定輸出檔案
            if not self.v2g_output_edit.text():
                output_path = str(Path(file_path).with_suffix(".gif"))
                self.v2g_output_edit.setText(output_path)

    def _browse_output_file_v2g(self):
        """瀏覽輸出檔案（影片轉 GIF）"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "選擇輸出 GIF 檔案", "", "GIF 檔案 (*.gif)"
        )
        if file_path:
            self.v2g_output_edit.setText(file_path)

    # === 轉換方法 ===

    def _update_progress(self, current: int, total: int):
        """更新進度條"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        percentage = int(current / total * 100) if total > 0 else 0
        self.status_label.setText(f"處理中... {percentage}%")

    def _on_task_finished(self, result: str):
        """任務完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("完成！")
        QMessageBox.information(self, "完成", f"轉換完成！\n{result}")
        self.worker = None

    def _on_task_error(self, error_msg: str):
        """任務錯誤"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("錯誤")
        QMessageBox.critical(self, "錯誤", f"轉換失敗：\n{error_msg}")
        self.worker = None

    def _start_video_to_images(self):
        """開始影片轉圖片"""
        video_path = self.v2i_input_edit.text().strip()
        output_dir = self.v2i_output_dir_edit.text().strip()

        if not video_path:
            QMessageBox.warning(self, "警告", "請選擇輸入影片檔案")
            return
        if not output_dir:
            QMessageBox.warning(self, "警告", "請選擇輸出目錄")
            return

        frame_interval = self.v2i_interval_spin.value()
        output_format = self.v2i_format_combo.currentText()

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("開始處理...")

        self.worker = WorkerThread(
            VideoConverter.video_to_images,
            video_path,
            output_dir,
            frame_interval,
            output_format,
            self._update_progress,
        )
        self.worker.finished.connect(self._on_task_finished)
        self.worker.error.connect(self._on_task_error)
        self.worker.start()

    def _start_images_to_media(self):
        """開始圖片轉媒體"""
        if not self.selected_images:
            QMessageBox.warning(self, "警告", "請新增至少一張圖片")
            return

        output_path = self.i2m_output_edit.text().strip()
        if not output_path:
            QMessageBox.warning(self, "警告", "請選擇輸出檔案")
            return

        fps = self.i2m_fps_spin.value()
        output_type = self.i2m_type_combo.currentText().lower()

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("開始處理...")

        if output_type == "gif":
            self.worker = WorkerThread(
                VideoConverter.images_to_gif,
                self.selected_images.copy(),
                output_path,
                float(fps),
                0,
                self._update_progress,
            )
        else:
            self.worker = WorkerThread(
                VideoConverter.images_to_video,
                self.selected_images.copy(),
                output_path,
                float(fps),
                "libx264",
                self._update_progress,
            )

        self.worker.finished.connect(self._on_task_finished)
        self.worker.error.connect(self._on_task_error)
        self.worker.start()

    def _start_video_to_gif(self):
        """開始影片轉 GIF"""
        video_path = self.v2g_input_edit.text().strip()
        output_path = self.v2g_output_edit.text().strip()

        if not video_path:
            QMessageBox.warning(self, "警告", "請選擇輸入影片檔案")
            return
        if not output_path:
            QMessageBox.warning(self, "警告", "請選擇輸出 GIF 檔案")
            return

        frame_interval = self.v2g_interval_spin.value()
        fps = self.v2g_fps_spin.value()
        max_width = self.v2g_max_width_spin.value()
        if max_width == 0:
            max_width = None

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("開始處理...")

        self.worker = WorkerThread(
            VideoConverter.video_to_gif,
            video_path,
            output_path,
            frame_interval,
            float(fps),
            max_width,
            self._update_progress,
        )
        self.worker.finished.connect(self._on_task_finished)
        self.worker.error.connect(self._on_task_error)
        self.worker.start()


def main():
    """主程式入口"""
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
