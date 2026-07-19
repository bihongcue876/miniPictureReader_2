"""ExifHandler 单元测试."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from core.exif_handler import ExifHandler


def _create_jpeg_with_exif(path: Path) -> Path:
    """创建带 EXIF 的 JPEG 测试文件."""
    img = Image.new("RGB", (100, 80), (255, 0, 0))
    # 构造简单 EXIF 数据
    import piexif

    zeroth = {
        piexif.ImageIFD.Make: "TestCamera",
        piexif.ImageIFD.Model: "TestModel",
        piexif.ImageIFD.Software: "TestSoft",
        piexif.ImageIFD.Artist: "TestAuthor",
        piexif.ImageIFD.Copyright: "TestCopyright",
    }
    exif_bytes = piexif.dump({"0th": zeroth})
    img.save(path, "JPEG", exif=exif_bytes)
    return path


class TestExifHandler:
    """EXIF 处理测试."""

    def test_read_exif_with_data(self, tmp_path: Path) -> None:
        jpg = _create_jpeg_with_exif(tmp_path / "test.jpg")
        result = ExifHandler.read_exif(jpg)

        basic = result.get("基本信息", {})
        assert basic["相机厂商"][1] == "TestCamera"
        assert basic["相机型号"][1] == "TestModel"
        assert basic["软件"][1] == "TestSoft"
        assert basic["作者"][1] == "TestAuthor"
        assert basic["版权信息"][1] == "TestCopyright"

    def test_read_exif_no_data(self, tmp_path: Path) -> None:
        """无 EXIF 的图片应返回空结构."""
        img = Image.new("RGB", (50, 50), (0, 255, 0))
        p = tmp_path / "noexif.png"
        img.save(p)
        result = ExifHandler.read_exif(p)
        # 应该返回分类的空字典
        assert "基本信息" in result
        assert "拍摄参数" in result
        assert "GPS" in result
        assert all(len(v) == 0 for v in result.values())

    def test_read_exif_nonexistent(self) -> None:
        result = ExifHandler.read_exif("nonexistent.jpg")
        assert "基本信息" in result
        assert all(len(v) == 0 for v in result.values())

    def test_write_exif(self, tmp_path: Path) -> None:
        jpg = _create_jpeg_with_exif(tmp_path / "test.jpg")

        # 修改版权信息
        ok = ExifHandler.write_exif(jpg, {"ImageCopyright": "NewCopyright"})
        assert ok

        # 验证写入成功
        result = ExifHandler.read_exif(jpg)
        assert result["基本信息"]["版权信息"][1] == "NewCopyright"

    def test_write_exif_to_nonexistent(self) -> None:
        ok = ExifHandler.write_exif(
            "nonexistent.jpg", {"ImageCopyright": "test"}
        )
        assert not ok

    def test_clear_exif(self, tmp_path: Path) -> None:
        jpg = _create_jpeg_with_exif(tmp_path / "test.jpg")

        ok = ExifHandler.clear_exif(jpg)
        assert ok

        result = ExifHandler.read_exif(jpg)
        assert all(len(v) == 0 for v in result.values())

    def test_clear_exif_nonexistent(self) -> None:
        ok = ExifHandler.clear_exif("nonexistent.jpg")
        assert not ok

    def test_gps_coordinates_no_gps(self, tmp_path: Path) -> None:
        jpg = _create_jpeg_with_exif(tmp_path / "test.jpg")
        coords = ExifHandler.get_gps_coordinates(jpg)
        assert coords is None

    def test_gps_coordinates_nonexistent(self) -> None:
        coords = ExifHandler.get_gps_coordinates("nonexistent.jpg")
        assert coords is None
