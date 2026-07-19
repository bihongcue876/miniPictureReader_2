"""插件接口定义 - 格式解析器和图像滤镜的扩展点."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from PIL import Image


class FormatPlugin(ABC):
    """格式解析器插件接口.

    实现此接口以支持自定义图片格式的加载.
    """

    @classmethod
    @abstractmethod
    def extensions(cls) -> list[str]:
        """插件支持的扩展名列表（含点号，如 '.foo'）."""
        ...

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """格式名称（如 'Foo Image'）."""
        ...

    @abstractmethod
    def load(self, path: str | Path) -> Image.Image:
        """加载图片并返回 PIL Image 对象."""
        ...

    @abstractmethod
    def can_load(self, path: str | Path) -> bool:
        """检查文件是否可由本插件加载."""
        ...


class FilterPlugin(ABC):
    """图像滤镜插件接口.

    实现此接口以提供自定义图像编辑滤镜.
    """

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """滤镜名称（如 'Vintage'）."""
        ...

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        """滤镜描述."""
        ...

    @abstractmethod
    def apply(self, image: Image.Image, **params: Any) -> Image.Image:
        """应用滤镜到图片.

        Args:
            image: 输入图片
            **params: 滤镜参数

        Returns:
            处理后的图片
        """
        ...


# ---------- 插件加载机制 ----------


def discover_plugins(
    plugin_dir: str | Path | None = None,
) -> dict[str, list[FormatPlugin | FilterPlugin]]:
    """发现并加载插件.

    Args:
        plugin_dir: 插件目录，默认为项目根目录下的 plugins/ 目录

    Returns:
        {"format": [FormatPlugin实例...], "filter": [FilterPlugin实例...]}
    """
    import importlib
    import inspect
    import pkgutil

    if plugin_dir is None:
        plugin_dir = Path(__file__).parent.parent / "plugins"
    else:
        plugin_dir = Path(plugin_dir)

    if not plugin_dir.is_dir():
        return {"format": [], "filter": []}

    # 确保插件目录在 sys.path 中
    import sys
    plugin_dir_str = str(plugin_dir)
    if plugin_dir_str not in sys.path:
        sys.path.insert(0, plugin_dir_str)

    formats: list[FormatPlugin] = []
    filters: list[FilterPlugin] = []

    for finder, name, is_pkg in pkgutil.iter_modules([plugin_dir_str]):
        if name.startswith("_"):
            continue

        try:
            module = importlib.import_module(name)
        except Exception:
            continue

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, FormatPlugin) and obj is not FormatPlugin:
                try:
                    formats.append(obj())
                except Exception:
                    pass
            elif issubclass(obj, FilterPlugin) and obj is not FilterPlugin:
                try:
                    filters.append(obj())
                except Exception:
                    pass

    return {"format": formats, "filter": filters}
