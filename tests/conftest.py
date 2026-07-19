"""pytest 测试夹具 - 生成测试用样本图片."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest
from PIL import Image


@pytest.fixture
def sample_images_dir(tmp_path: Path) -> Iterator[Path]:
    """生成各类格式的测试图片目录."""
    img_dir = tmp_path / "images"
    img_dir.mkdir()

    # RGB 测试图
    rgb = Image.new("RGB", (100, 80), (255, 0, 0))

    # JPEG
    rgb.save(img_dir / "test.jpg", "JPEG", quality=85)
    # PNG
    rgb.save(img_dir / "test.png", "PNG")
    # BMP
    rgb.save(img_dir / "test.bmp", "BMP")
    # TIFF
    rgb.save(img_dir / "test.tif", "TIFF")
    # WEBP
    rgb.save(img_dir / "test.webp", "WEBP")

    # GIF
    gif = Image.new("RGB", (50, 50), (0, 255, 0))
    gif.save(img_dir / "test.gif", "GIF")

    # PPM
    rgb.save(img_dir / "test.ppm", "PPM")

    # ICO
    ico = Image.new("RGBA", (32, 32), (0, 0, 255))
    ico.save(img_dir / "test.ico", "ICO")

    # 不支持的文件
    (img_dir / "unsupported.txt").write_text("not an image")

    yield img_dir


@pytest.fixture
def empty_dir(tmp_path: Path) -> Iterator[Path]:
    """空目录."""
    d = tmp_path / "empty"
    d.mkdir()
    yield d
