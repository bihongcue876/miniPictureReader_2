"""ImageLoader 单元测试."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.loader import (
    ImageLoader,
    ImageInfo,
    ImageLoadError,
    UnsupportedFormatError,
    ALL_EXTENSIONS,
    SUPPORTED_FORMATS,
)


class TestFormatDetection:
    """格式检测测试."""

    def test_all_formats_have_extensions(self) -> None:
        """确保每种格式都有扩展名."""
        for fmt, exts in SUPPORTED_FORMATS.items():
            assert len(exts) > 0, f"{fmt} 没有定义扩展名"
            for ext in exts:
                assert ext.startswith("."), f"{fmt} 的扩展名 {ext} 格式错误"

    def test_all_extensions_consolidated(self) -> None:
        """ALL_EXTENSIONS 包含所有格式的扩展名."""
        all_exts = set()
        for exts in SUPPORTED_FORMATS.values():
            all_exts.update(exts)
        assert set(ALL_EXTENSIONS) == all_exts


class TestIsSupported:
    """is_supported 方法测试."""

    def test_supported_format(self, sample_images_dir: Path) -> None:
        assert ImageLoader.is_supported(sample_images_dir / "test.jpg")
        assert ImageLoader.is_supported(sample_images_dir / "test.png")
        assert ImageLoader.is_supported(sample_images_dir / "test.bmp")
        assert ImageLoader.is_supported(sample_images_dir / "test.tif")
        assert ImageLoader.is_supported(sample_images_dir / "test.webp")

    def test_unsupported_format(self, sample_images_dir: Path) -> None:
        assert not ImageLoader.is_supported(
            sample_images_dir / "unsupported.txt"
        )

    def test_nonexistent_file(self) -> None:
        assert not ImageLoader.is_supported("nonexistent.jpg")

    def test_directory(self, tmp_path: Path) -> None:
        assert not ImageLoader.is_supported(tmp_path)


class TestLoad:
    """load 方法测试."""

    def test_load_jpeg(self, sample_images_dir: Path) -> None:
        info = ImageLoader.load(sample_images_dir / "test.jpg")
        assert isinstance(info, ImageInfo)
        assert info.format == "JPEG"
        assert info.size == (100, 80)

    def test_load_png(self, sample_images_dir: Path) -> None:
        info = ImageLoader.load(sample_images_dir / "test.png")
        assert info.format == "PNG"
        assert info.size == (100, 80)

    def test_load_metadata(self, sample_images_dir: Path) -> None:
        info = ImageLoader.load(sample_images_dir / "test.jpg")
        assert info.path.exists()
        assert info.path.is_absolute()
        assert info.file_size > 0
        assert info.modified is not None

    def test_load_nonexistent(self) -> None:
        with pytest.raises(ImageLoadError):
            ImageLoader.load("nonexistent.jpg")

    def test_load_unsupported_format(
        self, sample_images_dir: Path
    ) -> None:
        with pytest.raises(UnsupportedFormatError):
            ImageLoader.load(sample_images_dir / "unsupported.txt")


class TestLoadImage:
    """load_image 方法测试."""

    def test_load_image_pil(self, sample_images_dir: Path) -> None:
        from PIL import Image

        img = ImageLoader.load_image(sample_images_dir / "test.jpg")
        assert isinstance(img, Image.Image)
        assert img.size == (100, 80)

    def test_load_image_nonexistent(self) -> None:
        with pytest.raises(ImageLoadError):
            ImageLoader.load_image("nonexistent.jpg")


class TestThumbnail:
    """缩略图测试."""

    def test_thumbnail_size(self, sample_images_dir: Path) -> None:
        thumb = ImageLoader.get_thumbnail(
            sample_images_dir / "test.jpg", (64, 64)
        )
        # 缩略图应保持宽高比，且不超过 64x64
        w, h = thumb.size
        assert w <= 64
        assert h <= 64

    def test_thumbnail_default_size(
        self, sample_images_dir: Path
    ) -> None:
        thumb = ImageLoader.get_thumbnail(sample_images_dir / "test.png")
        w, h = thumb.size
        assert w <= 256
        assert h <= 256


class TestFormats:
    """格式列表测试."""

    def test_get_supported_formats(self) -> None:
        formats = ImageLoader.get_supported_formats()
        assert "JPEG" in formats
        assert "PNG" in formats
        assert len(formats) >= 6

    def test_get_format_extensions(self) -> None:
        exts = ImageLoader.get_format_extensions("JPEG")
        assert ".jpg" in exts
        assert ".jpeg" in exts

    def test_get_format_extensions_unknown(self) -> None:
        exts = ImageLoader.get_format_extensions("UNKNOWN")
        assert exts == ()
