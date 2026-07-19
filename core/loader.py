"""图片加载模块 - 负责图片格式检测、加载、缩略图生成."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageOps

# ---------- 支持格式定义 ----------

SUPPORTED_FORMATS: dict[str, tuple[str, ...]] = {
    "JPEG": (".jpg", ".jpeg", ".jpe", ".jfif"),
    "PNG": (".png",),
    "GIF": (".gif",),
    "BMP": (".bmp", ".dib"),
    "TIFF": (".tiff", ".tif"),
    "WEBP": (".webp",),
    "ICO": (".ico",),
    "PPM": (".ppm", ".pgm", ".pbm", ".pnm"),
}

ALL_EXTENSIONS: tuple[str, ...] = tuple(
    ext for exts in SUPPORTED_FORMATS.values() for ext in exts
)

# ---------- 数据类 ----------


@dataclass
class ImageInfo:
    """图片元数据."""

    path: Path
    format: str
    size: tuple[int, int]
    file_size: int
    modified: datetime


# ---------- 错误处理 ----------


class ImageLoadError(Exception):
    """图片加载异常."""


class UnsupportedFormatError(ImageLoadError):
    """不支持的图片格式."""


# ---------- 格式检测 ----------


def _detect_format_from_header(path: Path) -> str | None:
    """通过文件头检测真实格式."""
    try:
        with path.open("rb") as f:
            header = f.read(32)
    except OSError:
        return None

    # JPEG: FF D8 FF
    if header[:3] == b"\xff\xd8\xff":
        return "JPEG"
    # PNG: 89 50 4E 47
    if header[:4] == b"\x89PNG":
        return "PNG"
    # GIF: 47 49 46 38
    if header[:3] == b"GIF":
        return "GIF"
    # BMP: 42 4D
    if header[:2] == b"BM":
        return "BMP"
    # TIFF: 49 49 2A 00 或 4D 4D 00 2A
    if header[:4] in (b"II*\x00", b"MM\x00*"):
        return "TIFF"
    # WEBP: 52 49 46 46 xx xx xx xx 57 45 42 50
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "WEBP"
    # ICO: 00 00 01 00
    if header[:4] == b"\x00\x00\x01\x00":
        return "ICO"
    # PPM: P1/P2/P3/P4/P5/P6
    if header[:2] in (b"P1", b"P2", b"P3", b"P4", b"P5", b"P6"):
        return "PPM"

    return None


# ---------- 加载器 ----------


class ImageLoader:
    """图片加载器 - 统一接口."""

    @staticmethod
    def is_supported(path: str | Path) -> bool:
        """检查文件是否为支持的图片格式."""
        p = Path(path)
        if not p.is_file():
            return False
        ext = p.suffix.lower()
        return ext in ALL_EXTENSIONS

    @staticmethod
    def load(path: str | Path) -> ImageInfo:
        """加载图片并返回元数据."""
        p = Path(path)
        if not p.is_file():
            raise ImageLoadError(f"文件不存在: {path}")

        ext = p.suffix.lower()
        if ext not in ALL_EXTENSIONS:
            raise UnsupportedFormatError(f"不支持的格式: {ext}")

        # 用 PIL 打开验证
        try:
            with Image.open(p) as img:
                img.load()  # 确保数据可读
                fmt = img.format or _detect_format_from_header(p) or "UNKNOWN"
        except Exception as exc:
            raise ImageLoadError(f"无法解码图片: {path}") from exc

        stat = p.stat()
        return ImageInfo(
            path=p.resolve(),
            format=fmt,
            size=img.size,
            file_size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
        )

    @staticmethod
    def load_image(path: str | Path) -> Image.Image:
        """加载图片为 PIL Image 对象."""
        p = Path(path)
        if not p.is_file():
            raise ImageLoadError(f"文件不存在: {path}")
        try:
            return Image.open(p)
        except Exception as exc:
            raise ImageLoadError(f"无法解码图片: {path}") from exc

    @staticmethod
    def get_thumbnail(
        path: str | Path, size: tuple[int, int] = (256, 256)
    ) -> Image.Image:
        """生成缩略图."""
        img = ImageLoader.load_image(path)
        thumb = ImageOps.contain(img, size, Image.LANCZOS)
        return thumb

    @staticmethod
    def get_supported_formats() -> Sequence[str]:
        """获取支持的格式列表."""
        return tuple(SUPPORTED_FORMATS.keys())

    @staticmethod
    def get_format_extensions(format_name: str) -> tuple[str, ...]:
        """获取指定格式的扩展名列表."""
        return SUPPORTED_FORMATS.get(format_name.upper(), ())
