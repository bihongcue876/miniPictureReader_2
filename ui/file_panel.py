"""文件浏览面板 - 目录树 + 文件列表 + 格式筛选."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal, QDir, QStringListModel
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeView,
    QListView,
    QComboBox,
    QFileSystemModel,
    QLabel,
    QSplitter,
    QAbstractItemView,
    QSizePolicy,
)

from core.filters import FormatFilter, get_all_presets
from core.loader import ALL_EXTENSIONS


class FilePanel(QWidget):
    """文件浏览面板 - 包含目录树和文件列表."""

    file_selected = Signal(str)  # 文件选中信号
    file_activated = Signal(str)  # 文件双击打开信号

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._filter = FormatFilter()
        self._current_dir: Path | None = None

        self._setup_ui()
        self._connect_signals()

        # 默认筛选所有图片
        self._filter.set_from_preset(get_all_presets()[0])
        self._refresh_files()

    def _setup_ui(self) -> None:
        """构建界面."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 筛选器栏
        filter_layout = QHBoxLayout()
        filter_label = QLabel("筛选:")
        self._filter_combo = QComboBox()
        self._filter_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        for preset in get_all_presets():
            self._filter_combo.addItem(preset.name, preset)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self._filter_combo)
        layout.addLayout(filter_layout)

        # 分割器：目录树 + 文件列表
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 目录树
        self._dir_model = QFileSystemModel()
        self._dir_model.setRootPath(QDir.rootPath())
        self._dir_model.setFilter(
            QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot
        )

        self._tree_view = QTreeView()
        self._tree_view.setModel(self._dir_model)
        self._tree_view.setRootIndex(self._dir_model.index(QDir.rootPath()))
        self._tree_view.setAnimated(True)
        self._tree_view.setSortingEnabled(True)
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setColumnHidden(1, True)
        self._tree_view.setColumnHidden(2, True)
        self._tree_view.setColumnHidden(3, True)
        self._tree_view.hideColumn(1)
        self._tree_view.hideColumn(2)
        self._tree_view.hideColumn(3)
        splitter.addWidget(self._tree_view)

        # 文件列表
        self._file_model = QStringListModel()
        self._file_view = QListView()
        self._file_view.setModel(self._file_model)
        self._file_view.setViewMode(QListView.ViewMode.ListMode)
        self._file_view.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        splitter.addWidget(self._file_view)

        layout.addWidget(splitter)

    def _connect_signals(self) -> None:
        """连接信号."""
        self._tree_view.clicked.connect(self._on_directory_changed)
        self._file_view.clicked.connect(self._on_file_clicked)
        self._file_view.doubleClicked.connect(self._on_file_activated)
        self._filter_combo.currentIndexChanged.connect(self._on_filter_changed)

    # ---------- 目录导航 ----------

    def _on_directory_changed(self, index) -> None:
        """目录选择变化."""
        path = self._dir_model.filePath(index)
        self._current_dir = Path(path)
        self._refresh_files()

    def navigate_to(self, path: str | Path) -> None:
        """导航到指定目录."""
        p = Path(path)
        if p.is_dir():
            self._current_dir = p
            idx = self._dir_model.index(str(p))
            self._tree_view.setCurrentIndex(idx)
            self._tree_view.scrollTo(idx)
            self._refresh_files()

    # ---------- 文件列表 ----------

    def _refresh_files(self) -> None:
        """刷新文件列表."""
        if self._current_dir is None:
            self._file_model.setStringList([])
            return

        try:
            files = [
                f.name
                for f in sorted(self._current_dir.iterdir(), key=lambda x: x.name.lower())
                if f.is_file()
                and f.suffix.lower() in ALL_EXTENSIONS
                and self._filter.match(f)
            ]
        except PermissionError:
            files = []

        self._file_model.setStringList(files)

    def _on_filter_changed(self, index: int) -> None:
        """筛选条件变化."""
        preset_data = self._filter_combo.itemData(index)
        if preset_data is not None:
            self._filter.set_from_preset(preset_data)
        self._refresh_files()

    def _on_file_clicked(self, index) -> None:
        """文件单击."""
        name = self._file_model.data(index, Qt.ItemDataRole.DisplayRole)
        if name and self._current_dir:
            path = str(self._current_dir / name)
            self.file_selected.emit(path)

    def _on_file_activated(self, index) -> None:
        """文件双击."""
        name = self._file_model.data(index, Qt.ItemDataRole.DisplayRole)
        if name and self._current_dir:
            path = str(self._current_dir / name)
            self.file_activated.emit(path)

    # ---------- 公共方法 ----------

    @property
    def current_directory(self) -> Path | None:
        return self._current_dir

    def current_files(self) -> list[str]:
        """获取当前文件列表."""
        return self._file_model.stringList()

    def refresh(self) -> None:
        """刷新当前目录."""
        self._refresh_files()
