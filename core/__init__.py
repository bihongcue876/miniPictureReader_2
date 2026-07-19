"""PictureReader 核心逻辑层 - 纯 Python，零 GUI 依赖."""

from core.loader import ImageLoader, ImageInfo
from core.filters import FormatFilter, FilterPreset
from core.exif_handler import ExifHandler
from core.editor import ImageEditor
from core.raw_loader import RawLoader, RawInfo, RawLoadError
from core.batch import BatchProcessor, BatchSummary, BatchResult
from core.interfaces import FormatPlugin, FilterPlugin, discover_plugins

__all__ = [
    "ImageLoader",
    "ImageInfo",
    "FormatFilter",
    "FilterPreset",
    "ExifHandler",
    "ImageEditor",
    "RawLoader",
    "RawInfo",
    "RawLoadError",
    "BatchProcessor",
    "BatchSummary",
    "BatchResult",
    "FormatPlugin",
    "FilterPlugin",
    "discover_plugins",
]
