"""批处理对话框 - 批量格式转换/调整大小/重命名."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QTextEdit,
    QTabWidget,
    QWidget,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QGridLayout,
)

from core.batch import BatchProcessor, BatchSummary
from core.loader import ALL_EXTENSIONS


class _BatchWorker(QThread):
    """后台批处理工作线程."""

    progress = Signal(int, int, str)
    finished = Signal(object)
    error = Signal(str)

    def __init__(
        self, operation: str, files: list[str], **kwargs
    ) -> None:
        super().__init__()
        self._operation = operation
        self._files = files
        self._kwargs = kwargs

    def run(self) -> None:
        try:
            if self._operation == "convert":
                result = BatchProcessor.convert(
                    self._files,
                    progress=self._on_progress,
                    **self._kwargs,
                )
            elif self._operation == "resize":
                result = BatchProcessor.resize(
                    self._files,
                    progress=self._on_progress,
                    **self._kwargs,
                )
            elif self._operation == "rename":
                result = BatchProcessor.rename(
                    self._files,
                    progress=self._on_progress,
                    **self._kwargs,
                )
            else:
                self.error.emit(f"未知操作: {self._operation}")
                return
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _on_progress(self, current: int, total: int, name: str) -> None:
        self.progress.emit(current, total, name)


class BatchDialog(QDialog):
    """批处理对话框."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._files: list[str] = []
        self._worker: _BatchWorker | None = None
        self.setWindowTitle("批处理")
        self.setMinimumSize(600, 500)
        self._setup_ui()

    def set_files(self, files: Sequence[str | Path]) -> None:
        """设置待处理的文件列表."""
        self._files = [str(f) for f in files]
        self._file_count_label.setText(f"已选择 {len(self._files)} 个文件")

    def _setup_ui(self) -> None:
        """构建界面."""
        layout = QVBoxLayout(self)

        # 文件信息
        self._file_count_label = QLabel("未选择文件")
        layout.addWidget(self._file_count_label)

        select_btn = QPushButton("选择文件...")
        select_btn.clicked.connect(self._select_files)
        layout.addWidget(select_btn)

        # 选项卡
        tabs = QTabWidget()

        # 格式转换
        convert_widget = self._build_convert_tab()
        tabs.addTab(convert_widget, "格式转换")

        # 调整大小
        resize_widget = self._build_resize_tab()
        tabs.addTab(resize_widget, "调整大小")

        # 重命名
        rename_widget = self._build_rename_tab()
        tabs.addTab(rename_widget, "重命名")

        layout.addWidget(tabs)

        # 进度
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        self._status_label = QLabel()
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

        # 日志
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(120)
        self._log.setVisible(False)
        layout.addWidget(self._log)

        # 按钮
        btn_layout = QHBoxLayout()
        self._start_btn = QPushButton("开始处理")
        self._start_btn.clicked.connect(self._start)
        self._start_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "font-weight: bold; padding: 8px 20px; }"
        )
        btn_layout.addStretch()
        btn_layout.addWidget(self._start_btn)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _build_convert_tab(self) -> QWidget:
        """格式转换选项卡."""
        w = QWidget()
        form = QFormLayout(w)

        self._convert_format = QComboBox()
        self._convert_format.addItems(["JPEG", "PNG", "BMP", "TIFF", "WEBP"])
        form.addRow("目标格式:", self._convert_format)

        self._convert_output = QLineEdit()
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(
            lambda: self._browse_output(self._convert_output)
        )
        row = QHBoxLayout()
        row.addWidget(self._convert_output)
        row.addWidget(browse_btn)
        form.addRow("输出目录:", row)

        return w

    def _build_resize_tab(self) -> QWidget:
        """调整大小选项卡."""
        w = QWidget()
        form = QFormLayout(w)

        self._resize_width = QSpinBox()
        self._resize_width.setRange(1, 10000)
        self._resize_width.setValue(1920)
        form.addRow("宽度 (px):", self._resize_width)

        self._resize_height = QSpinBox()
        self._resize_height.setRange(1, 10000)
        self._resize_height.setValue(1080)
        form.addRow("高度 (px):", self._resize_height)

        self._keep_aspect = QCheckBox("保持宽高比")
        self._keep_aspect.setChecked(True)
        form.addRow("", self._keep_aspect)

        self._resize_output = QLineEdit()
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(
            lambda: self._browse_output(self._resize_output)
        )
        row = QHBoxLayout()
        row.addWidget(self._resize_output)
        row.addWidget(browse_btn)
        form.addRow("输出目录:", row)

        return w

    def _build_rename_tab(self) -> QWidget:
        """重命名选项卡."""
        w = QWidget()
        form = QFormLayout(w)

        help_label = QLabel(
            "使用 {n} 表示序号，{i} 表示索引 (0起始)\n"
            '例如: "photo_{n:03d}" → photo_001, photo_002, ...'
        )
        help_label.setStyleSheet("color: #666;")
        form.addRow(help_label)

        self._rename_pattern = QLineEdit("photo_{n:03d}")
        form.addRow("命名模板:", self._rename_pattern)

        self._rename_start = QSpinBox()
        self._rename_start.setRange(0, 9999)
        self._rename_start.setValue(1)
        form.addRow("起始编号:", self._rename_start)

        self._dry_run = QCheckBox("仅预览（不实际重命名）")
        form.addRow("", self._dry_run)

        return w

    # ---------- 操作 ----------

    def _select_files(self) -> None:
        """选择文件对话框."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片文件", "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff *.webp)"
        )
        if files:
            self._files = files
            self._file_count_label.setText(f"已选择 {len(self._files)} 个文件")

    def _browse_output(self, line_edit: QLineEdit) -> None:
        """选择输出目录."""
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            line_edit.setText(folder)

    def _start(self) -> None:
        """开始批处理."""
        if not self._files:
            QMessageBox.warning(self, "提示", "请先选择文件")
            return

        current_tab = self.findChild(QTabWidget).currentIndex()

        # 获取参数
        kwargs = {}
        operation = ""
        if current_tab == 0:  # 转换
            output = self._convert_output.text()
            if not output:
                QMessageBox.warning(self, "提示", "请选择输出目录")
                return
            kwargs = {
                "output_dir": output,
                "target_format": self._convert_format.currentText(),
            }
            operation = "convert"
        elif current_tab == 1:  # 调整大小
            output = self._resize_output.text()
            if not output:
                QMessageBox.warning(self, "提示", "请选择输出目录")
                return
            kwargs = {
                "output_dir": output,
                "size": (self._resize_width.value(), self._resize_height.value()),
                "keep_aspect": self._keep_aspect.isChecked(),
            }
            operation = "resize"
        elif current_tab == 2:  # 重命名
            kwargs = {
                "pattern": self._rename_pattern.text(),
                "start_number": self._rename_start.value(),
                "dry_run": self._dry_run.isChecked(),
            }
            operation = "rename"

        # 禁用按钮
        self._start_btn.setEnabled(False)
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._status_label.setVisible(True)
        self._status_label.setText("准备中...")
        self._log.setVisible(True)
        self._log.clear()

        # 启动工作线程
        self._worker = _BatchWorker(operation, self._files, **kwargs)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, current: int, total: int, name: str) -> None:
        """进度更新."""
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(current)
        self._status_label.setText(f"处理中 ({current}/{total}): {name}")
        self._log.append(f"[{current}/{total}] {name}")

    def _on_finished(self, summary: BatchSummary) -> None:
        """处理完成."""
        self._start_btn.setEnabled(True)
        self._progress_bar.setValue(summary.total)
        self._status_label.setText(
            f"完成! 成功: {summary.succeeded}, 失败: {summary.failed}"
        )
        self._log.append(
            f"\n处理完成: {summary.total} 个文件, "
            f"{summary.succeeded} 成功, {summary.failed} 失败"
        )

        for r in summary.results:
            if not r.success:
                self._log.append(f"  ✗ {r.path.name}: {r.error}")

    def _on_error(self, msg: str) -> None:
        """处理出错."""
        self._start_btn.setEnabled(True)
        self._status_label.setText(f"出错: {msg}")
        self._log.append(f"\n错误: {msg}")
