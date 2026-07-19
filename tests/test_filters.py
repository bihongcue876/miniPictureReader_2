"""FormatFilter 单元测试."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.filters import FormatFilter, FilterPreset, get_all_presets, get_preset


class TestFilterPreset:
    """筛选预设测试."""

    def test_get_all_presets(self) -> None:
        presets = get_all_presets()
        assert len(presets) >= 6
        names = [p.name for p in presets]
        assert "所有图片" in names
        assert "JPEG" in names

    def test_get_preset_exists(self) -> None:
        preset = get_preset("all")
        assert preset is not None
        assert preset.name == "所有图片"
        assert "JPEG" in preset.formats

    def test_get_preset_not_found(self) -> None:
        assert get_preset("nonexistent") is None

    def test_custom_preset(self) -> None:
        preset = FilterPreset(
            name="自定义", formats=["JPEG", "PNG"], is_custom=True
        )
        assert preset.is_custom
        assert "JPEG" in preset.formats
        assert "PNG" in preset.formats


class TestFormatFilter:
    """FormatFilter 功能测试."""

    def test_default_no_filter(self) -> None:
        f = FormatFilter()
        assert f.match("test.jpg")
        assert f.match("test.txt")

    def test_filter_jpeg_only(self) -> None:
        preset = get_preset("jpeg")
        assert preset is not None
        f = FormatFilter(preset)
        assert f.match("test.jpg")
        assert f.match("test.JPG")
        assert not f.match("test.png")
        assert not f.match("test.bmp")

    def test_filter_png_only(self) -> None:
        preset = get_preset("png")
        assert preset is not None
        f = FormatFilter(preset)
        assert f.match("test.png")
        assert not f.match("test.jpg")

    def test_set_formats(self) -> None:
        f = FormatFilter()
        f.set_formats(["JPEG", "PNG"])
        assert f.match("test.jpg")
        assert f.match("test.png")
        assert not f.match("test.webp")

    def test_add_remove_format(self) -> None:
        f = FormatFilter()
        f.set_formats(["JPEG"])
        f.add_format("PNG")
        assert "PNG" in f.active_formats
        f.remove_format("JPEG")
        assert "JPEG" not in f.active_formats

    def test_clear(self) -> None:
        f = FormatFilter(get_preset("jpeg"))
        f.clear()
        assert list(f.active_formats) == []
        assert f.match("any.txt")

    def test_filter_files(self, sample_images_dir: Path) -> None:
        files = list(sample_images_dir.iterdir())
        f = FormatFilter(get_preset("jpeg"))
        matched = f.filter_files(files)
        assert len(matched) == 1
        assert matched[0].suffix.lower() == ".jpg"

    def test_all_formats_filter(self, sample_images_dir: Path) -> None:
        files = list(sample_images_dir.iterdir())
        f = FormatFilter(get_preset("all"))
        matched = f.filter_files(files)
        # 应匹配所有图片文件，但不包括 unsupported.txt
        image_count = sum(
            1 for f in files if f.suffix.lower() != ".txt"
        )
        assert len(matched) == image_count  # 所有图片文件应全匹配
