"""EXIF 信息展示与编辑面板."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QHeaderView,
    QGroupBox,
    QMessageBox,
    QAbstractItemView,
    QSizePolicy,
)

from core.exif_handler import ExifHandler


class ExifPanel(QWidget):
    """EXIF 信息面板 - 展示和编辑 EXIF 元数据."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._current_path: Path | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """构建界面."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # 标题
        title = QLabel("EXIF 信息")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        # 表格
        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["字段", "值"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        layout.addWidget(self._table, 1)

        # 操作按钮
        btn_layout = QHBoxLayout()

        self._edit_btn = QPushButton("编辑选中")
        self._edit_btn.setEnabled(False)
        btn_layout.addWidget(self._edit_btn)

        self._save_btn = QPushButton("保存修改")
        self._save_btn.setEnabled(False)
        btn_layout.addWidget(self._save_btn)

        self._clear_btn = QPushButton("清除 EXIF")
        self._clear_btn.setEnabled(False)
        btn_layout.addWidget(self._clear_btn)

        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.setEnabled(False)
        btn_layout.addWidget(self._refresh_btn)

        layout.addLayout(btn_layout)

        # 连接信号
        self._edit_btn.clicked.connect(self._on_edit_selected)
        self._save_btn.clicked.connect(self._on_save)
        self._clear_btn.clicked.connect(self._on_clear)
        self._refresh_btn.clicked.connect(self._on_refresh)

    # ---------- 公共方法 ----------

    def show_exif(self, path: str | Path) -> None:
        """显示指定图片的 EXIF 数据."""
        self._current_path = Path(path)
        self._refresh_display()

    def clear(self) -> None:
        """清空显示."""
        self._current_path = None
        self._table.setRowCount(0)
        self._clear_state()

    def _clear_state(self) -> None:
        """禁用所有按钮."""
        self._edit_btn.setEnabled(False)
        self._save_btn.setEnabled(False)
        self._clear_btn.setEnabled(False)
        self._refresh_btn.setEnabled(False)

    def _refresh_display(self) -> None:
        """刷新 EXIF 显示."""
        if self._current_path is None:
            return

        data = ExifHandler.read_exif(self._current_path)
        self._table.setRowCount(0)

        has_data = False
        for category, fields in data.items():
            if not fields:
                continue
            has_data = True

            # 分类标题行
            row = self._table.rowCount()
            self._table.insertRow(row)
            cat_item = QTableWidgetItem(f"【{category}】")
            bold_font = cat_item.font()
            bold_font.setBold(True)
            cat_item.setFont(bold_font)
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self._table.setItem(row, 0, cat_item)
            self._table.setItem(row, 1, QTableWidgetItem(""))

            # 字段行
            for label, (key, value, editable) in fields.items():
                row = self._table.rowCount()
                self._table.insertRow(row)

                name_item = QTableWidgetItem(label)
                name_item.setToolTip(key)
                key_item = QTableWidgetItem(value)
                if editable:
                    # 可编辑字段用蓝色标记
                    name_item.setForeground(Qt.GlobalColor.blue)
                    key_item.setForeground(Qt.GlobalColor.blue)

                self._table.setItem(row, 0, name_item)
                self._table.setItem(row, 1, key_item)

        if not has_data:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(
                row, 0, QTableWidgetItem("(无 EXIF 数据)")
            )

        self._edit_btn.setEnabled(has_data)
        self._clear_btn.setEnabled(has_data)
        self._refresh_btn.setEnabled(True)

    # ---------- 编辑操作 ----------

    def _on_edit_selected(self) -> None:
        """编辑选中的可编辑字段."""
        current_row = self._table.currentRow()
        if current_row < 0:
            return

        key_item = self._table.item(current_row, 0)
        value_item = self._table.item(current_row, 1)
        if not key_item or not value_item:
            return

        # 只有标记为蓝色的可编辑字段才能编辑
        if key_item.foreground() != Qt.GlobalColor.blue:
            return

        self._table.editItem(value_item)
        self._save_btn.setEnabled(True)

    def _on_save(self) -> None:
        """保存所有修改过的 EXIF 字段."""
        if self._current_path is None:
            return

        updates: dict[str, str] = {}
        for row in range(self._table.rowCount()):
            key_item = self._table.item(row, 0)
            value_item = self._table.item(row, 1)
            tooltip = key_item.toolTip() if key_item else ""
            if tooltip and value_item and key_item:
                # 检查是否被用户修改过（对比原始数据）
                updates[tooltip] = value_item.text()

        if not updates:
            return

        ok = ExifHandler.write_exif(self._current_path, updates)
        if ok:
            QMessageBox.information(self, "保存成功", "EXIF 数据已更新")
            self._save_btn.setEnabled(False)
            self._refresh_display()
        else:
            QMessageBox.warning(self, "保存失败", "无法写入 EXIF 数据")

    def _on_clear(self) -> None:
        """清除所有 EXIF 数据."""
        if self._current_path is None:
            return

        reply = QMessageBox.question(
            self,
            "确认清除",
            "确定要清除所有 EXIF 数据吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ok = ExifHandler.clear_exif(self._current_path)
            if ok:
                QMessageBox.information(self, "清除成功", "EXIF 数据已清除")
                self._refresh_display()
            else:
                QMessageBox.warning(self, "清除失败", "无法清除 EXIF 数据")

    def _on_refresh(self) -> None:
        """刷新显示."""
        if self._current_path:
            self._refresh_display()
