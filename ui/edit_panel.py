"""编辑工具栏 - 旋转、翻转、裁剪、图像调整."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QSizePolicy,
)

from core.editor import ImageEditor


class EditPanel(QWidget):
    """编辑工具栏面板."""

    rotate_left_clicked = Signal()
    rotate_right_clicked = Signal()
    flip_horizontal_clicked = Signal()
    flip_vertical_clicked = Signal()
    crop_clicked = Signal()
    undo_clicked = Signal()
    redo_clicked = Signal()
    reset_clicked = Signal()
    save_clicked = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """构建界面."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # 标题
        title = QLabel("编辑工具")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        # 旋转
        layout.addWidget(self._make_section_label("旋转"))
        rotate_layout = QHBoxLayout()
        self._rot_left_btn = QPushButton("↺ 左旋")
        self._rot_right_btn = QPushButton("↻ 右旋")
        rotate_layout.addWidget(self._rot_left_btn)
        rotate_layout.addWidget(self._rot_right_btn)
        layout.addLayout(rotate_layout)

        # 翻转
        layout.addWidget(self._make_section_label("翻转"))
        flip_layout = QHBoxLayout()
        self._flip_h_btn = QPushButton("↔ 水平")
        self._flip_v_btn = QPushButton("↕ 垂直")
        flip_layout.addWidget(self._flip_h_btn)
        flip_layout.addWidget(self._flip_v_btn)
        layout.addLayout(flip_layout)

        # 裁剪
        layout.addWidget(self._make_section_label("裁剪"))
        self._crop_btn = QPushButton("✂ 裁剪模式")
        layout.addWidget(self._crop_btn)

        # 分割线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep)

        # 撤销/重做
        undo_redo_layout = QHBoxLayout()
        self._undo_btn = QPushButton("↩ 撤销")
        self._undo_btn.setEnabled(False)
        self._redo_btn = QPushButton("↪ 重做")
        self._redo_btn.setEnabled(False)
        undo_redo_layout.addWidget(self._undo_btn)
        undo_redo_layout.addWidget(self._redo_btn)
        layout.addLayout(undo_redo_layout)

        # 重置
        self._reset_btn = QPushButton("⟲ 重置")
        self._reset_btn.setEnabled(False)
        layout.addWidget(self._reset_btn)

        # 保存
        self._save_btn = QPushButton("💾 保存")
        self._save_btn.setEnabled(False)
        self._save_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "font-weight: bold; padding: 6px; }"
        )
        layout.addWidget(self._save_btn)

        layout.addStretch()

        # 连接信号
        self._rot_left_btn.clicked.connect(self.rotate_left_clicked.emit)
        self._rot_right_btn.clicked.connect(self.rotate_right_clicked.emit)
        self._flip_h_btn.clicked.connect(self.flip_horizontal_clicked.emit)
        self._flip_v_btn.clicked.connect(self.flip_vertical_clicked.emit)
        self._crop_btn.clicked.connect(self.crop_clicked.emit)
        self._undo_btn.clicked.connect(self.undo_clicked.emit)
        self._redo_btn.clicked.connect(self.redo_clicked.emit)
        self._reset_btn.clicked.connect(self.reset_clicked.emit)
        self._save_btn.clicked.connect(self.save_clicked.emit)

    def _make_section_label(self, text: str) -> QLabel:
        """创建小节标签."""
        label = QLabel(text)
        label.setStyleSheet("color: #666; font-size: 11px;")
        return label

    # ---------- 状态更新 ----------

    def update_undo_redo_state(
        self, can_undo: bool, can_redo: bool
    ) -> None:
        """更新撤销/重做按钮状态."""
        self._undo_btn.setEnabled(can_undo)
        self._redo_btn.setEnabled(can_redo)
        self._reset_btn.setEnabled(can_undo or can_redo)
        self._save_btn.setEnabled(can_undo or can_redo)
