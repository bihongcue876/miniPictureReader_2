"""主窗口 - 应用入口界面."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QApplication,
    QTabWidget,
    QSizePolicy,
)

from ui.viewer import ImageViewer
from ui.file_panel import FilePanel
from ui.exif_panel import ExifPanel
from ui.edit_panel import EditPanel
from ui.adjust_panel import AdjustPanel
from ui.thumb_view import ThumbView
from ui.slideshow import SlideshowWindow
from core.editor import ImageEditor


class MainWindow(QMainWindow):
    """主窗口."""

    def __init__(self) -> None:
        super().__init__()
        self._settings = QSettings("PictureReader", "PictureReader")
        self._file_list: list[str] = []
        self._current_index: int = -1
        self._editor: ImageEditor | None = None

        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._connect_signals()
        self._restore_state()

    def _setup_ui(self) -> None:
        """构建主界面."""
        self.setWindowTitle("PictureReader")
        self.setMinimumSize(1000, 600)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        h_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧文件面板
        self._file_panel = FilePanel()
        self._file_panel.setMinimumWidth(180)
        self._file_panel.setMaximumWidth(350)
        h_splitter.addWidget(self._file_panel)

        # 中央区域
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # 视图切换标签
        self._view_tabs = QTabWidget()
        self._view_tabs.setDocumentMode(True)

        # 单个图片查看器
        self._viewer = ImageViewer()
        self._view_tabs.addTab(self._viewer, "单图查看")

        # 缩略图网格
        self._thumb_view = ThumbView()
        self._view_tabs.addTab(self._thumb_view, "缩略图")

        center_layout.addWidget(self._view_tabs, 1)

        # 编辑工具栏 + 调整面板
        edit_row = QHBoxLayout()
        edit_row.setSpacing(0)

        self._edit_panel = EditPanel()
        edit_row.addWidget(self._edit_panel)

        self._adjust_panel = AdjustPanel()
        edit_row.addWidget(self._adjust_panel)

        center_layout.addLayout(edit_row)

        h_splitter.addWidget(center_widget)

        # 右侧EXIF面板
        self._exif_panel = ExifPanel()
        self._exif_panel.setMinimumWidth(200)
        self._exif_panel.setMaximumWidth(400)
        h_splitter.addWidget(self._exif_panel)

        h_splitter.setStretchFactor(0, 0)
        h_splitter.setStretchFactor(1, 1)
        h_splitter.setStretchFactor(2, 0)

        main_layout.addWidget(h_splitter)

    def _setup_menu(self) -> None:
        """构建菜单栏."""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        open_act = QAction("打开文件夹...(&O)", self)
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.triggered.connect(self._open_folder)
        file_menu.addAction(open_act)

        file_menu.addSeparator()

        save_act = QAction("保存(&S)", self)
        save_act.setShortcut(QKeySequence("Ctrl+S"))
        save_act.triggered.connect(self._on_save)
        file_menu.addAction(save_act)

        save_as_act = QAction("另存为...(&A)", self)
        save_as_act.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_act.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_act)

        file_menu.addSeparator()

        # 文件管理
        rename_act = QAction("重命名...(&R)", self)
        rename_act.setShortcut(QKeySequence("F2"))
        rename_act.triggered.connect(self._on_rename)
        file_menu.addAction(rename_act)

        delete_act = QAction("删除(&D)", self)
        delete_act.setShortcut(QKeySequence("Delete"))
        delete_act.triggered.connect(self._on_delete)
        file_menu.addAction(delete_act)

        show_in_explorer_act = QAction("在文件管理器中显示(&E)", self)
        show_in_explorer_act.triggered.connect(self._on_show_in_explorer)
        file_menu.addAction(show_in_explorer_act)

        file_menu.addSeparator()

        batch_act = QAction("批处理...(&B)", self)
        batch_act.setShortcut(QKeySequence("Ctrl+B"))
        batch_act.triggered.connect(self._on_batch)
        file_menu.addAction(batch_act)

        file_menu.addSeparator()

        exit_act = QAction("退出(&Q)", self)
        exit_act.setShortcut(QKeySequence("Ctrl+Q"))
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        undo_act = QAction("撤销(&U)", self)
        undo_act.setShortcut(QKeySequence("Ctrl+Z"))
        undo_act.triggered.connect(self._on_undo)
        edit_menu.addAction(undo_act)

        redo_act = QAction("重做(&R)", self)
        redo_act.setShortcut(QKeySequence("Ctrl+Y"))
        redo_act.triggered.connect(self._on_redo)
        edit_menu.addAction(redo_act)

        edit_menu.addSeparator()
        rot_left_act = QAction("左旋 90°", self)
        rot_left_act.triggered.connect(self._on_rotate_left)
        edit_menu.addAction(rot_left_act)
        rot_right_act = QAction("右旋 90°", self)
        rot_right_act.triggered.connect(self._on_rotate_right)
        edit_menu.addAction(rot_right_act)
        flip_h_act = QAction("水平翻转", self)
        flip_h_act.triggered.connect(self._on_flip_horizontal)
        edit_menu.addAction(flip_h_act)
        flip_v_act = QAction("垂直翻转", self)
        flip_v_act.triggered.connect(self._on_flip_vertical)
        edit_menu.addAction(flip_v_act)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        fit_act = QAction("适应窗口(&F)", self)
        fit_act.setShortcut(QKeySequence("Ctrl+0"))
        fit_act.triggered.connect(self._viewer.fit_to_window)
        view_menu.addAction(fit_act)
        actual_act = QAction("原始大小(&A)", self)
        actual_act.setShortcut(QKeySequence("Ctrl+1"))
        actual_act.triggered.connect(self._viewer.actual_size)
        view_menu.addAction(actual_act)
        view_menu.addSeparator()
        zoom_in_act = QAction("放大(&I)", self)
        zoom_in_act.setShortcut(QKeySequence("Ctrl++"))
        zoom_in_act.triggered.connect(self._viewer.zoom_in)
        view_menu.addAction(zoom_in_act)
        zoom_out_act = QAction("缩小(&O)", self)
        zoom_out_act.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_act.triggered.connect(self._viewer.zoom_out)
        view_menu.addAction(zoom_out_act)
        view_menu.addSeparator()

        thumb_act = QAction("缩略图模式(&T)", self)
        thumb_act.setShortcut(QKeySequence("Ctrl+T"))
        thumb_act.triggered.connect(lambda: self._view_tabs.setCurrentIndex(1))
        view_menu.addAction(thumb_act)

        slideshow_act = QAction("幻灯片播放(&S)", self)
        slideshow_act.setShortcut(QKeySequence("F5"))
        slideshow_act.triggered.connect(self._on_slideshow)
        view_menu.addAction(slideshow_act)

        # 导航菜单
        nav_menu = menubar.addMenu("导航(&N)")
        prev_act = QAction("上一张(&P)", self)
        prev_act.setShortcut(QKeySequence(Qt.Key.Key_Left))
        prev_act.triggered.connect(self._navigate_prev)
        nav_menu.addAction(prev_act)
        next_act = QAction("下一张(&N)", self)
        next_act.setShortcut(QKeySequence(Qt.Key.Key_Right))
        next_act.triggered.connect(self._navigate_next)
        nav_menu.addAction(next_act)
        nav_menu.addSeparator()
        first_act = QAction("首张", self)
        first_act.setShortcut(QKeySequence(Qt.Key.Key_Home))
        first_act.triggered.connect(self._navigate_first)
        nav_menu.addAction(first_act)
        last_act = QAction("末张", self)
        last_act.setShortcut(QKeySequence(Qt.Key.Key_End))
        last_act.triggered.connect(self._navigate_last)
        nav_menu.addAction(last_act)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        about_act = QAction("关于 PictureReader(&A)", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    def _setup_statusbar(self) -> None:
        """构建状态栏."""
        self._status_label = QLabel()
        self._zoom_label = QLabel()
        self._zoom_label.setMinimumWidth(100)
        self._zoom_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.statusBar().addWidget(self._status_label, 1)
        self.statusBar().addPermanentWidget(self._zoom_label)

    def _connect_signals(self) -> None:
        """连接信号."""
        # 文件面板
        self._file_panel.file_activated.connect(self._on_file_activated)
        self._file_panel.file_selected.connect(self._on_file_selected)

        # 查看器
        self._viewer.zoom_changed.connect(self._on_zoom_changed)

        # 缩略图
        self._thumb_view.file_activated.connect(self._on_file_activated)

        # 视图切换
        self._view_tabs.currentChanged.connect(self._on_view_tab_changed)

        # 编辑面板
        self._edit_panel.rotate_left_clicked.connect(self._on_rotate_left)
        self._edit_panel.rotate_right_clicked.connect(self._on_rotate_right)
        self._edit_panel.flip_horizontal_clicked.connect(self._on_flip_horizontal)
        self._edit_panel.flip_vertical_clicked.connect(self._on_flip_vertical)
        self._edit_panel.undo_clicked.connect(self._on_undo)
        self._edit_panel.redo_clicked.connect(self._on_redo)
        self._edit_panel.reset_clicked.connect(self._on_reset)
        self._edit_panel.save_clicked.connect(self._on_save)

        # 调整面板
        self._adjust_panel.brightness_changed.connect(self._on_brightness)
        self._adjust_panel.contrast_changed.connect(self._on_contrast)
        self._adjust_panel.saturation_changed.connect(self._on_saturation)
        self._adjust_panel.auto_optimize_clicked.connect(self._on_auto_optimize)
        self._adjust_panel.reset_clicked.connect(self._on_adjust_reset)

    # ---------- 文件操作 ----------

    def _open_folder(self) -> None:
        """打开文件夹对话框."""
        folder = QFileDialog.getExistingDirectory(
            self, "选择图片文件夹", str(self._file_panel.current_directory or "")
        )
        if folder:
            self._file_panel.navigate_to(folder)
            self._update_file_list()
            self._thumb_view.load_directory(folder)

    def _update_file_list(self) -> None:
        """更新当前文件列表."""
        self._file_list = self._file_panel.current_files()
        self._current_index = -1

    def _on_file_activated(self, path: str) -> None:
        """文件双击/激活."""
        self._view_tabs.setCurrentIndex(0)  # 切换到单图模式
        self._load_and_display(path)
        self._update_current_index(path)

    def _on_file_selected(self, path: str) -> None:
        """文件单击."""
        self._update_current_index(path)

    def _update_current_index(self, path: str) -> None:
        p = Path(path)
        files = self._file_panel.current_files()
        try:
            self._current_index = files.index(p.name)
        except ValueError:
            self._current_index = -1

    def _on_view_tab_changed(self, index: int) -> None:
        """视图标签切换."""
        if index == 1:  # 缩略图模式
            directory = self._file_panel.current_directory
            if directory:
                self._thumb_view.load_directory(directory)

    def _load_and_display(self, path: str) -> None:
        """加载并显示图片."""
        if self._viewer.load_image(path):
            p = Path(path)
            self.setWindowTitle(f"PictureReader - {p.name}")
            self._update_status(p)
            self._update_file_list()

            # 初始化编辑器
            try:
                pil_image = Image.open(p)
                self._editor = ImageEditor(pil_image)
                # 更新直方图
                self._update_histogram()
            except Exception:
                self._editor = None

            self._exif_panel.show_exif(p)
            self._edit_panel.update_undo_redo_state(False, False)
            self._adjust_panel.set_sliders_default()

    def _update_status(self, path: Path) -> None:
        try:
            info = path.stat()
            size = info.st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / 1024 / 1024:.1f} MB"
            self._status_label.setText(f"{path.name}  |  {size_str}")
        except OSError:
            self._status_label.setText(path.name)

    def _on_zoom_changed(self, zoom: float) -> None:
        self._zoom_label.setText(f"缩放: {zoom}%")

    # ---------- 文件管理 ----------

    def _on_rename(self) -> None:
        """重命名当前文件."""
        if self._viewer.current_path is None:
            return
        old = self._viewer.current_path
        name, ok = QInputDialog.getText(
            self, "重命名", "新文件名:", text=old.stem
        )
        if ok and name:
            new_path = old.with_stem(name)
            try:
                old.rename(new_path)
                self._load_and_display(str(new_path))
                self._file_panel.refresh()
            except OSError as e:
                QMessageBox.warning(self, "重命名失败", str(e))

    def _on_delete(self) -> None:
        """删除当前文件到回收站."""
        if self._viewer.current_path is None:
            return
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {self._viewer.current_path.name} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                import send2trash
                send2trash.send2trash(str(self._viewer.current_path))
            except ImportError:
                self._viewer.current_path.unlink()
            self._file_panel.refresh()
            self._viewer.clear_image()
            self._exif_panel.clear()
            self._editor = None

    def _on_show_in_explorer(self) -> None:
        """在文件管理器中显示."""
        if self._viewer.current_path is None:
            return
        path = self._viewer.current_path
        import sys
        if sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path.parent)])

    # ---------- 幻灯片 ----------

    def _on_slideshow(self) -> None:
        """启动幻灯片播放."""
        directory = self._file_panel.current_directory
        if not directory:
            return
        files = [
            str(f) for f in sorted(directory.iterdir())
            if f.is_file() and f.suffix.lower() in (
                ".jpg", ".jpeg", ".png", ".bmp", ".gif",
                ".tif", ".tiff", ".webp",
            )
        ]
        if not files:
            return
        start = max(0, self._current_index)
        self._slideshow = SlideshowWindow(files, start)
        self._slideshow.show()

    # ---------- 批处理 ----------

    def _on_batch(self) -> None:
        """打开批处理对话框."""
        from ui.batch_dialog import BatchDialog

        dialog = BatchDialog(self)
        directory = self._file_panel.current_directory
        if directory:
            try:
                files = [
                    str(f) for f in sorted(directory.iterdir())
                    if f.is_file() and f.suffix.lower() in (
                        ".jpg", ".jpeg", ".png", ".bmp", ".gif",
                        ".tif", ".tiff", ".webp",
                    )
                ]
                dialog.set_files(files)
            except PermissionError:
                pass
        dialog.exec()

    # ---------- 编辑操作 ----------

    def _apply_editor_to_viewer(self) -> None:
        if self._editor is None:
            return
        from PIL.ImageQt import ImageQt
        from PySide6.QtGui import QPixmap

        qimage = ImageQt(self._editor.image)
        pixmap = QPixmap.fromImage(qimage)
        self._viewer.display_pixmap(pixmap)
        self._edit_panel.update_undo_redo_state(
            self._editor.can_undo, self._editor.can_redo
        )
        self._update_histogram()

    def _update_histogram(self) -> None:
        """更新直方图."""
        if self._editor is None:
            return
        try:
            r, g, b = self._editor.histogram()
            self._adjust_panel.update_histogram(r, g, b)
        except Exception:
            pass

    def _on_rotate_left(self) -> None:
        if self._editor is None:
            return
        self._editor.rotate(270)
        self._apply_editor_to_viewer()

    def _on_rotate_right(self) -> None:
        if self._editor is None:
            return
        self._editor.rotate(90)
        self._apply_editor_to_viewer()

    def _on_flip_horizontal(self) -> None:
        if self._editor is None:
            return
        self._editor.flip("horizontal")
        self._apply_editor_to_viewer()

    def _on_flip_vertical(self) -> None:
        if self._editor is None:
            return
        self._editor.flip("vertical")
        self._apply_editor_to_viewer()

    def _on_undo(self) -> None:
        if self._editor is None:
            return
        self._editor.undo()
        self._apply_editor_to_viewer()

    def _on_redo(self) -> None:
        if self._editor is None:
            return
        self._editor.redo()
        self._apply_editor_to_viewer()

    def _on_reset(self) -> None:
        if self._editor is None:
            return
        self._editor.reset()
        self._apply_editor_to_viewer()

    def _on_save(self) -> None:
        if self._editor is None or self._viewer.current_path is None:
            return
        ok = self._editor.save_overwrite(self._viewer.current_path)
        if ok:
            QMessageBox.information(self, "保存成功", "图片已保存")
            self._edit_panel.update_undo_redo_state(
                self._editor.can_undo, self._editor.can_redo
            )
        else:
            QMessageBox.warning(self, "保存失败", "无法保存图片")

    def _on_save_as(self) -> None:
        if self._editor is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", "", "JPEG (*.jpg);;PNG (*.png);;BMP (*.bmp)"
        )
        if path:
            ok = self._editor.save_overwrite(path)
            if ok:
                QMessageBox.information(self, "保存成功", f"图片已保存到 {path}")
            else:
                QMessageBox.warning(self, "保存失败", "无法保存图片")

    # ---------- 图像调整 ----------

    def _on_brightness(self, factor: float) -> None:
        if self._editor is None:
            return
        self._editor.adjust_brightness(factor)
        self._apply_editor_to_viewer()

    def _on_contrast(self, factor: float) -> None:
        if self._editor is None:
            return
        self._editor.adjust_contrast(factor)
        self._apply_editor_to_viewer()

    def _on_saturation(self, factor: float) -> None:
        if self._editor is None:
            return
        self._editor.adjust_saturation(factor)
        self._apply_editor_to_viewer()

    def _on_auto_optimize(self) -> None:
        if self._editor is None:
            return
        self._editor.auto_optimize()
        self._apply_editor_to_viewer()
        self._adjust_panel.set_sliders_default()

    def _on_adjust_reset(self) -> None:
        if self._editor is None:
            return
        # 重置所有图像调整：撤销到原始状态
        while self._editor.can_undo:
            self._editor.undo()
        self._apply_editor_to_viewer()
        self._adjust_panel.set_sliders_default()

    # ---------- 导航 ----------

    def _navigate_prev(self) -> None:
        if self._current_index > 0:
            self._current_index -= 1
            self._open_by_index()

    def _navigate_next(self) -> None:
        if self._current_index < len(self._file_list) - 1:
            self._current_index += 1
            self._open_by_index()
        elif self._file_list:
            self._current_index = 0
            self._open_by_index()

    def _navigate_first(self) -> None:
        if self._file_list:
            self._current_index = 0
            self._open_by_index()

    def _navigate_last(self) -> None:
        if self._file_list:
            self._current_index = len(self._file_list) - 1
            self._open_by_index()

    def _open_by_index(self) -> None:
        if 0 <= self._current_index < len(self._file_list):
            name = self._file_list[self._current_index]
            directory = self._file_panel.current_directory
            if directory:
                path = str(directory / name)
                self._load_and_display(path)

    # ---------- 对话框 ----------

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "关于 PictureReader",
            "PictureReader v0.1.0\n\n"
            "轻量级跨平台图片查看与管理工具\n\n"
            "技术栈: Python + PySide6 + Pillow",
        )

    # ---------- 状态持久化 ----------

    def _restore_state(self) -> None:
        geometry = self._settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        state = self._settings.value("windowState")
        if state is not None:
            self.restoreState(state)

    def closeEvent(self, event) -> None:
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.setValue("windowState", self.saveState())
        super().closeEvent(event)
