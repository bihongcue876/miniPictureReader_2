"""缩略图网格浏览组件."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Sequence

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
    QLabel,
    QSlider,
    QHBoxLayout,
    QSizePolicy,
)

from core.loader import ImageLoader, ALL_EXTENSIONS


class _ThumbLabel(QLabel):
    """缩略图标签 - 可响应点击."""

    clicked = Signal(str)

    def __init__(self, path: str, pixmap: QPixmap, name: str) -> None:
        super().__init__()
        self._path = path
        self.setPixmap(
            pixmap.scaled(
                120, 120, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setToolTip(name)
        self.setStyleSheet(
            "QLabel { border: 1px solid #ccc; padding: 4px; "
            "border-radius: 4px; background: #fafafa; }"
            "QLabel:hover { border-color: #4A90D9; background: #e8f0fe; }"
        )
        self.setFixedSize(140, 140)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self._path)
        super().mousePressEvent(event)


class ThumbView(QWidget):
    """缩略图网格浏览."""

    file_activated = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._directory: Path | None = None
        self._thumb_size = 120
        self._setup_ui()

    def _setup_ui(self) -> None:
        """构建界面."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 缩略图大小滑块
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("小"))
        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setRange(60, 200)
        self._size_slider.setValue(self._thumb_size)
        self._size_slider.valueChanged.connect(self._on_size_changed)
        slider_layout.addWidget(self._size_slider)
        slider_layout.addWidget(QLabel("大"))
        layout.addLayout(slider_layout)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(8)
        scroll.setWidget(self._grid_widget)

        layout.addWidget(scroll, 1)

    # ---------- 数据加载 ----------

    def load_directory(self, path: str | Path) -> None:
        """加载指定目录的缩略图."""
        self._directory = Path(path)
        self._clear_grid()
        self._populate_grid()

    def _clear_grid(self) -> None:
        """清除网格."""
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def _populate_grid(self) -> None:
        """填充缩略图网格."""
        if self._directory is None:
            return

        try:
            files = sorted(
                [f for f in self._directory.iterdir()
                 if f.is_file() and f.suffix.lower() in ALL_EXTENSIONS],
                key=lambda x: x.name.lower(),
            )
        except PermissionError:
            return

        cols = max(1, self.width() // (self._thumb_size + 20))

        for i, f in enumerate(files):
            row = i // cols
            col = i % cols

            pixmap = self._get_cached_thumbnail(f)
            label = _ThumbLabel(str(f), pixmap, f.name)
            label.clicked.connect(self._on_thumb_clicked)
            self._grid_layout.addWidget(label, row, col)

    @lru_cache(maxsize=256)
    def _get_cached_thumbnail(self, path: Path) -> QPixmap:
        """带缓存的缩略图加载."""
        size = (self._thumb_size, self._thumb_size)
        try:
            pil_thumb = ImageLoader.get_thumbnail(path, size)
            from PIL.ImageQt import ImageQt
            from PySide6.QtGui import QImage

            qimage = ImageQt(pil_thumb)
            return QPixmap.fromImage(qimage)
        except Exception:
            return QPixmap()

    # ---------- 交互 ----------

    def _on_thumb_clicked(self, path: str) -> None:
        """缩略图点击."""
        self.file_activated.emit(path)

    def _on_size_changed(self, value: int) -> None:
        """缩略图大小变化."""
        self._thumb_size = value
        self._get_cached_thumbnail.cache_clear()
        self._populate_grid()

    def resizeEvent(self, event) -> None:
        """窗口大小变化时重新布局."""
        super().resizeEvent(event)
        if self._directory:
            self._populate_grid()

    def refresh(self) -> None:
        """刷新当前目录."""
        self._get_cached_thumbnail.cache_clear()
        if self._directory:
            self._populate_grid()
