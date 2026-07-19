"""图片查看组件 - 基于 QGraphicsView 实现缩放和平移."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QWheelEvent, QMouseEvent, QPixmap, QPainter, QCursor
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QApplication,
)

from core.loader import ImageLoader


class ImageViewer(QGraphicsView):
    """图片查看器 - 支持缩放、平移."""

    zoom_changed = Signal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._current_pixmap: QPixmap | None = None
        self._current_path: Path | None = None
        self._fit_mode = True

        self._setup_view()

    def _setup_view(self) -> None:
        """初始化视图设置."""
        self.setRenderHints(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.SmartViewportUpdate
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setBackgroundBrush(self.palette().window())
        self.setFrameShape(self.frameShape().NoFrame)

        # 初始化空场景提示
        self._scene.addText("打开文件夹选择图片", QApplication.font())

    # ---------- 图片加载 ----------

    def load_image(self, path: str | Path) -> bool:
        """加载并显示图片."""
        p = Path(path)
        if not p.is_file():
            return False

        pixmap = QPixmap(str(p))
        if pixmap.isNull():
            return False

        self._current_path = p
        self._current_pixmap = pixmap
        self._update_display()
        return True

    def display_pixmap(self, pixmap: QPixmap) -> None:
        """直接显示 QPixmap（用于编辑器结果展示）."""
        self._current_pixmap = pixmap
        self._current_path = None  # 编辑器修改后路径可能已变
        self._update_display()

    def _update_display(self) -> None:
        """在场景中显示当前图片."""
        if self._current_pixmap is None:
            return

        self._scene.clear()
        self._pixmap_item = QGraphicsPixmapItem(self._current_pixmap)
        self._pixmap_item.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )
        self._scene.addItem(self._pixmap_item)
        self._scene.setSceneRect(
            QRectF(self._current_pixmap.rect())
        )

        if self._fit_mode:
            self.fit_to_window()

    # ---------- 缩放 ----------

    def fit_to_window(self) -> None:
        """自适应窗口大小."""
        if self._pixmap_item is None:
            return
        self._fit_mode = True
        self.resetTransform()
        self.fitInView(
            self._pixmap_item,
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self._emit_zoom()

    def actual_size(self) -> None:
        """1:1 原始大小显示."""
        if self._pixmap_item is None:
            return
        self._fit_mode = False
        self.resetTransform()
        self._emit_zoom()

    def zoom_in(self) -> None:
        """放大."""
        self._zoom_by(1.25)

    def zoom_out(self) -> None:
        """缩小."""
        self._zoom_by(0.8)

    def _zoom_by(self, factor: float) -> None:
        """按比例缩放."""
        self._fit_mode = False
        new_zoom = self.transform().m11() * factor
        if 0.01 <= new_zoom <= 32.0:
            self.scale(factor, factor)
            self._emit_zoom()

    def _emit_zoom(self) -> None:
        """发射缩放比例信号."""
        zoom = self.transform().m11() * 100
        self.zoom_changed.emit(round(zoom, 1))

    # ---------- 事件重写 ----------

    def wheelEvent(self, event: QWheelEvent) -> None:
        """滚轮缩放."""
        if self._pixmap_item is None:
            super().wheelEvent(event)
            return

        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self._zoom_by(factor)
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """双击切换自适应/原始大小."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._fit_mode:
                self.actual_size()
            else:
                self.fit_to_window()
        super().mouseDoubleClickEvent(event)

    def resizeEvent(self, event) -> None:
        """窗口大小变化时保持自适应."""
        super().resizeEvent(event)
        if self._fit_mode and self._pixmap_item is not None:
            self.fit_to_window()

    # ---------- 属性 ----------

    @property
    def current_path(self) -> Path | None:
        return self._current_path

    @property
    def has_image(self) -> bool:
        return self._current_pixmap is not None

    def clear_image(self) -> None:
        """清除当前图片."""
        self._scene.clear()
        self._current_pixmap = None
        self._current_path = None
        self._fit_mode = True
        self.resetTransform()
        self._scene.addText("打开文件夹选择图片", QApplication.font())
