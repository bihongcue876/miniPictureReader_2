"""图像调整面板 - 亮度/对比度/饱和度滑块 + 直方图."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QFrame,
    QSizePolicy,
)


class _HistogramWidget(QWidget):
    """直方图绘制组件."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._hist_r: list[int] | None = None
        self._hist_g: list[int] | None = None
        self._hist_b: list[int] | None = None
        self.setMinimumHeight(100)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

    def set_histogram(
        self,
        r: list[int],
        g: list[int],
        b: list[int],
    ) -> None:
        """设置直方图数据."""
        self._hist_r = r
        self._hist_g = g
        self._hist_b = b
        self.update()

    def clear(self) -> None:
        """清空直方图."""
        self._hist_r = self._hist_g = self._hist_b = None
        self.update()

    def paintEvent(self, event) -> None:
        """绘制直方图."""
        super().paintEvent(event)
        if self._hist_r is None:
            return

        painter = QPainter(self)
        w = self.width()
        h = self.height()
        margin = 4

        # 背景
        painter.fillRect(
            0, 0, w, h, QColor(30, 30, 30)
        )

        draw_h = h - 2 * margin
        bar_w = max(1, (w - 2 * margin) // 256)

        # 找最大值用于归一化
        max_val = 1
        for hist in (self._hist_r, self._hist_g, self._hist_b):
            if hist:
                max_val = max(max_val, max(hist))

        # 绘制各通道
        colors = [
            (QColor(255, 60, 60, 160), self._hist_r),   # R
            (QColor(60, 255, 60, 160), self._hist_g),   # G
            (QColor(60, 60, 255, 160), self._hist_b),   # B
        ]

        for color, hist in colors:
            if not hist:
                continue
            painter.setPen(QPen(color, bar_w))
            for i in range(256):
                val = hist[i] * draw_h // max_val
                x = margin + i * bar_w
                y = h - margin - val
                painter.drawLine(x, y, x, h - margin)

        painter.end()


class AdjustPanel(QWidget):
    """图像调整面板."""

    brightness_changed = Signal(float)
    contrast_changed = Signal(float)
    saturation_changed = Signal(float)
    auto_optimize_clicked = Signal()
    reset_clicked = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """构建界面."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # 标题
        title = QLabel("图像调整")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        # 直方图
        self._hist_widget = _HistogramWidget()
        layout.addWidget(self._hist_widget)

        # 分割线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep)

        # 亮度
        self._add_slider(
            layout, "亮度", self.brightness_changed,
            -100, 100, 0, 50,
        )

        # 对比度
        self._add_slider(
            layout, "对比度", self.contrast_changed,
            -100, 100, 0, 50,
        )

        # 饱和度
        self._add_slider(
            layout, "饱和度", self.saturation_changed,
            -100, 100, 0, 50,
        )

        # 按钮
        btn_layout = QHBoxLayout()

        self._auto_btn = QPushButton("✨ 自动优化")
        self._auto_btn.clicked.connect(
            self.auto_optimize_clicked.emit
        )
        btn_layout.addWidget(self._auto_btn)

        self._reset_btn = QPushButton("↺ 重置")
        self._reset_btn.clicked.connect(self.reset_clicked.emit)
        btn_layout.addWidget(self._reset_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def _add_slider(
        self,
        layout: QVBoxLayout,
        name: str,
        signal: Signal,
        min_val: int,
        max_val: int,
        default: int,
        tick_interval: int,
    ) -> None:
        """添加一个滑块行."""
        row = QHBoxLayout()

        label = QLabel(name)
        label.setFixedWidth(50)
        row.addWidget(label)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(tick_interval)

        value_label = QLabel(f"{default}")
        value_label.setFixedWidth(40)
        value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        slider.valueChanged.connect(
            lambda v: (
                value_label.setText(f"{v:+d}"),
                signal.emit(v / 100.0 + 1.0),
            )
        )

        row.addWidget(slider)
        row.addWidget(value_label)
        layout.addLayout(row)

    def set_sliders_default(self) -> None:
        """重置滑块到默认值."""
        # 查找所有滑块并重置
        for child in self.findChildren(QSlider):
            child.setValue(0)

    def update_histogram(
        self,
        r: list[int],
        g: list[int],
        b: list[int],
    ) -> None:
        """更新直方图."""
        self._hist_widget.set_histogram(r, g, b)

    def clear_histogram(self) -> None:
        """清空直方图."""
        self._hist_widget.clear()
