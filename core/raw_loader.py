"""RAW 格式解码模块 - 支持主流相机 RAW 格式."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image

from core.loader import ImageLoadError, SUPPORTED_FORMATS

# ---------- RAW 扩展名定义 ----------

RAW_EXTENSIONS: dict[str, tuple[str, ...]] = {
    "RAW_CR2": (".cr2", ".cr3"),
    "RAW_NEF": (".nef", ".nrf"),
    "RAW_ARW": (".arw", ".srf", ".sr2"),
    "RAW_RAF": (".raf",),
    "RAW_DNG": (".dng",),
    "RAW_RW2": (".rw2",),
    "RAW_ORF": (".orf",),
    "RAW_PEF": (".pef",),
}

ALL_RAW_EXTENSIONS: tuple[str, ...] = tuple(
    ext for exts in RAW_EXTENSIONS.values() for ext in exts
)

# ---------- 尝试导入 RawPy ----------

try:
    import rawpy
    _HAS_RAWPY = True
except ImportError:
    _HAS_RAWPY = False


@dataclass
class RawInfo:
    """RAW 文件元数据."""

    path: Path
    raw_type: str
    thumb_size: tuple[int, int] | None
    full_size: tuple[int, int] | None


class RawLoadError(ImageLoadError):
    """RAW 加载异常."""


class RawLoader:
    """RAW 文件加载器."""

    @staticmethod
    def is_available() -> bool:
        """检查 RawPy 是否可用."""
        return _HAS_RAWPY

    @staticmethod
    def is_raw(path: str | Path) -> bool:
        """检查文件是否为 RAW 格式."""
        return Path(path).suffix.lower() in ALL_RAW_EXTENSIONS

    @staticmethod
    def load_preview(
        path: str | Path,
    ) -> Image.Image | None:
        """加载 RAW 文件的嵌入式 JPEG 预览图.

        快速模式 - 不需要完整解码 RAW 数据.
        """
        if not _HAS_RAWPY:
            raise RawLoadError("RawPy 未安装，无法加载 RAW 文件")

        p = Path(path)
        if not p.is_file():
            raise RawLoadError(f"文件不存在: {path}")

        try:
            with rawpy.imread(str(p)) as raw:
                thumb = raw.extract_thumb()
                if thumb.format == rawpy.ThumbFormat.JPEG:
                    return Image.open(thumb.data)
                # 如果是位图格式
                return Image.frombuffer(
                    "RGB", (thumb.width, thumb.height), thumb.data
                )
        except Exception as exc:
            raise RawLoadError(f"无法解码 RAW 预览图: {path}") from exc

    @staticmethod
    def load_full(
        path: str | Path,
        white_balance: tuple[float, float, float, float] | None = None,
        brightness: float = 1.0,
    ) -> Image.Image:
        """完整解码 RAW 文件.

        Args:
            path: RAW 文件路径
            white_balance: (r, g1, b, g2) 白平衡系数，None 使用相机设置
            brightness: 亮度补偿倍数

        Returns:
            解码后的 PIL Image (RGB 模式)
        """
        if not _HAS_RAWPY:
            raise RawLoadError("RawPy 未安装，无法加载 RAW 文件")

        p = Path(path)
        if not p.is_file():
            raise RawLoadError(f"文件不存在: {path}")

        try:
            with rawpy.imread(str(p)) as raw:
                # 基本解码后处理参数
                postproc = rawpy.PostprocessingParameters(
                    output_color=rawpy.ColorSpace.sRGB,
                    user_black=None,
                    user_sat=None,
                    no_auto_bright=False,
                    bright=brightness,
                )

                # 应用白平衡
                if white_balance is not None:
                    raw.white_balance = white_balance

                rgb = raw.postprocess(postproc)
                return Image.fromarray(rgb)
        except Exception as exc:
            raise RawLoadError(f"无法解码 RAW 文件: {path}") from exc

    @staticmethod
    def load(path: str | Path) -> Image.Image:
        """智能加载 - 先尝试预览图，失败则完整解码."""
        try:
            preview = RawLoader.load_preview(path)
            if preview is not None:
                return preview
        except (RawLoadError, Exception):
            pass

        return RawLoader.load_full(path)

    @staticmethod
    def get_info(path: str | Path) -> RawInfo:
        """获取 RAW 文件元数据."""
        if not _HAS_RAWPY:
            raise RawLoadError("RawPy 未安装")

        p = Path(path)
        if not p.is_file():
            raise RawLoadError(f"文件不存在: {path}")

        raw_type = "UNKNOWN"
        ext = p.suffix.lower()
        for fmt, exts in RAW_EXTENSIONS.items():
            if ext in exts:
                raw_type = fmt
                break

        try:
            with rawpy.imread(str(p)) as raw:
                thumb_size: tuple[int, int] | None = None
                try:
                    thumb = raw.extract_thumb()
                    thumb_size = (thumb.width, thumb.height)
                except Exception:
                    pass

                full_size = (raw.sizes.width, raw.sizes.height)
        except Exception as exc:
            raise RawLoadError(f"无法读取 RAW 信息: {path}") from exc

        return RawInfo(
            path=p.resolve(),
            raw_type=raw_type,
            thumb_size=thumb_size,
            full_size=full_size,
        )

    @staticmethod
    def get_supported_raw_formats() -> Sequence[str]:
        """获取支持的 RAW 格式列表."""
        return tuple(RAW_EXTENSIONS.keys())
