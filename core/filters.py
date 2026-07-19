"""格式筛选模块 - 定义筛选预设和匹配逻辑."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from core.loader import SUPPORTED_FORMATS


@dataclass
class FilterPreset:
    """筛选预设."""

    name: str
    formats: list[str]
    is_custom: bool = False


# ---------- 预设筛选器 ----------

_PRESETS: dict[str, FilterPreset] = {
    "all": FilterPreset(name="所有图片", formats=list(SUPPORTED_FORMATS.keys())),
    "jpeg": FilterPreset(name="JPEG", formats=["JPEG"]),
    "png": FilterPreset(name="PNG", formats=["PNG"]),
    "webp": FilterPreset(name="WebP", formats=["WEBP"]),
    "bitmap": FilterPreset(name="位图 (BMP)", formats=["BMP"]),
    "tiff": FilterPreset(name="TIFF", formats=["TIFF"]),
    "gif": FilterPreset(name="GIF", formats=["GIF"]),
}


def get_all_presets() -> Sequence[FilterPreset]:
    """获取所有预设筛选器."""
    return tuple(_PRESETS.values())


def get_preset(name: str) -> FilterPreset | None:
    """按名称获取预设."""
    return _PRESETS.get(name)


# ---------- 扩展名映射 ----------

_FORMAT_EXT_MAP: dict[str, tuple[str, ...]] = SUPPORTED_FORMATS


# ---------- 筛选逻辑 ----------


class FormatFilter:
    """格式筛选器."""

    def __init__(self, preset: FilterPreset | None = None) -> None:
        self._formats: set[str] = set()
        if preset is not None:
            self.set_from_preset(preset)

    def set_from_preset(self, preset: FilterPreset) -> None:
        """从预设设置筛选条件."""
        self._formats = set(preset.formats)

    def set_formats(self, formats: list[str]) -> None:
        """直接设置筛选的格式列表."""
        self._formats = set(formats)

    def add_format(self, fmt: str) -> None:
        """添加一个格式到筛选."""
        self._formats.add(fmt.upper())

    def remove_format(self, fmt: str) -> None:
        """移除一个格式."""
        self._formats.discard(fmt.upper())

    def match(self, path: str | Path) -> bool:
        """判断文件是否匹配当前筛选条件."""
        if not self._formats:
            return True

        p = Path(path)
        ext = p.suffix.lower()

        for fmt in self._formats:
            exts = _FORMAT_EXT_MAP.get(fmt.upper(), ())
            if ext in exts:
                return True
        return False

    def filter_files(self, files: Sequence[str | Path]) -> list[Path]:
        """过滤文件列表，返回匹配的文件."""
        return [Path(f) for f in files if self.match(f)]

    @property
    def active_formats(self) -> Sequence[str]:
        """当前激活的格式列表."""
        return tuple(self._formats)

    def clear(self) -> None:
        """清除所有筛选条件."""
        self._formats.clear()
