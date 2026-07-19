"""幻灯片播放窗口."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPixmap, QKeyEvent, QResizeEvent
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QCheckBox,
    QApplication,
)

from core.loader import ALL_EXTENSIONS, ImageLoader


class SlideshowWindow(QWidget):
    """全屏幻灯片窗口."""

    def __init__(
        self, files: list[str], start_index: int = 0
    ) -> None:
        super().__init__()
        self._files = files
        self._current_index = start_index
        self._interval = 3000  # 默认 3 秒
        self._shuffle = False
        self._paused = False
        self._played_indices: set[int] = set()

        self._setup_ui()
        self._setup_timer()
        self._load_current()

    def _setup_ui(self) -> None:
        """构建界面."""
        self.setWindowTitle("幻灯片播放")
        self.setCursor(Qt.CursorShape.BlankCursor)

        # 全屏
        self.showFullScreen()

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 图片显示
        self._image_label = QLabel()
        self._image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self._image_label.setStyleSheet("background-color: black;")
        layout.addWidget(self._image_label, 1)

        # 控制栏（鼠标移动时显示）
        self._control_bar = QWidget()
        self._control_bar.setStyleSheet(
            "QWidget { background-color: rgba(0,0,0,180); "
            "border-radius: 8px; }"
            "QPushButton { color: white; background: transparent; "
            "border: 1px solid #666; padding: 6px 14px; "
            "border-radius: 4px; font-size: 14px; }"
            "QPushButton:hover { background: #444; }"
            "QLabel { color: white; }"
        )
        control_layout = QHBoxLayout(self._control_bar)
        control_layout.setContentsMargins(10, 6, 10, 6)

        self._prev_btn = QPushButton("◀ 上一张")
        self._prev_btn.clicked.connect(self._prev)
        control_layout.addWidget(self._prev_btn)

        self._play_pause_btn = QPushButton("⏸ 暂停")
        self._play_pause_btn.clicked.connect(self._toggle_pause)
        control_layout.addWidget(self._play_pause_btn)

        self._next_btn = QPushButton("下一张 ▶")
        self._next_btn.clicked.connect(self._next)
        control_layout.addWidget(self._next_btn)

        control_layout.addSpacing(20)

        control_layout.addWidget(QLabel("间隔:"))
        self._interval_slider = QSlider(Qt.Orientation.Horizontal)
        self._interval_slider.setRange(1, 10)
        self._interval_slider.setValue(3)
        self._interval_slider.setFixedWidth(120)
        self._interval_slider.valueChanged.connect(
            self._on_interval_changed
        )
        control_layout.addWidget(self._interval_slider)
        self._interval_label = QLabel("3s")
        control_layout.addWidget(self._interval_label)

        self._shuffle_cb = QCheckBox("随机")
        self._shuffle_cb.setStyleSheet("color: white;")
        self._shuffle_cb.toggled.connect(self._on_shuffle_toggled)
        control_layout.addWidget(self._shuffle_cb)

        control_layout.addStretch()

        self._info_label = QLabel()
        control_layout.addWidget(self._info_label)

        exit_btn = QPushButton("✕ 退出")
        exit_btn.clicked.connect(self.close)
        control_layout.addWidget(exit_btn)

        layout.addWidget(self._control_bar)

        # 控制栏自动隐藏定时器
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(
            lambda: self._control_bar.hide()
        )

    def _setup_timer(self) -> None:
        """设置切换定时器."""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next)
        self._timer.start(self._interval)

    # ---------- 图片加载 ----------

    def _load_current(self) -> None:
        """加载当前图片."""
        if not self._files:
            return

        if 0 <= self._current_index < len(self._files):
            path = self._files[self._current_index]
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self._image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._image_label.setPixmap(scaled)

            name = Path(path).name
            total = len(self._files)
            self._info_label.setText(
                f"{self._current_index + 1}/{total}  {name}"
            )

    def resizeEvent(self, event: QResizeEvent) -> None:
        """窗口大小变化时重新缩放."""
        super().resizeEvent(event)
        self._load_current()

    # ---------- 导航 ----------

    def _next(self) -> None:
        """下一张."""
        if not self._files:
            return

        if self._shuffle:
            import random

            remaining = [
                i for i in range(len(self._files))
                if i not in self._played_indices
            ]
            if not remaining:
                self._played_indices.clear()
                remaining = list(range(len(self._files)))

            self._current_index = random.choice(remaining)
        else:
            self._current_index = (self._current_index + 1) % len(self._files)

        self._played_indices.add(self._current_index)
        self._load_current()

    def _prev(self) -> None:
        """上一张."""
        if not self._files:
            return
        self._current_index = (
            self._current_index - 1
        ) % len(self._files)
        self._load_current()

    def _toggle_pause(self) -> None:
        """暂停/继续."""
        if self._paused:
            self._timer.start(self._interval)
            self._play_pause_btn.setText("⏸ 暂停")
        else:
            self._timer.stop()
            self._play_pause_btn.setText("▶ 继续")
        self._paused = not self._paused

    # ---------- 配置 ----------

    def _on_interval_changed(self, value: int) -> None:
        """间隔时间变化."""
        self._interval = value * 1000
        self._interval_label.setText(f"{value}s")
        if not self._paused:
            self._timer.start(self._interval)

    def _on_shuffle_toggled(self, checked: bool) -> None:
        """随机模式切换."""
        self._shuffle = checked
        if checked:
            self._played_indices.clear()

    # ---------- 键盘控制 ----------

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """键盘控制."""
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()
            case Qt.Key.Key_Space:
                self._toggle_pause()
            case Qt.Key.Key_Right | Qt.Key.Key_Down:
                self._next()
            case Qt.Key.Key_Left | Qt.Key.Key_Up:
                self._prev()
            case _:
                super().keyPressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """鼠标移动时显示控制栏."""
        self._control_bar.show()
        self._hide_timer.start(3000)
        super().mouseMoveEvent(event)
