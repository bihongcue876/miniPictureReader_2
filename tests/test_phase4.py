"""Phase 4 测试 - RAW/批处理/插件."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from core.batch import BatchProcessor
from core.interfaces import discover_plugins
from core.raw_loader import RawLoader, RawLoadError, ALL_RAW_EXTENSIONS


# ========== RAW 加载测试 ==========


class TestRawLoader:
    """RAW 加载测试（rawpy 可能未安装）."""

    def test_is_available(self) -> None:
        """检查 rawpy 是否可用."""
        # 不应抛出异常
        available = RawLoader.is_available()
        assert isinstance(available, bool)

    def test_is_raw_true(self) -> None:
        assert RawLoader.is_raw("photo.CR2")
        assert RawLoader.is_raw("photo.nef")
        assert RawLoader.is_raw("photo.ARW")
        assert RawLoader.is_raw("photo.dng")

    def test_is_raw_false(self) -> None:
        assert not RawLoader.is_raw("photo.jpg")
        assert not RawLoader.is_raw("photo.png")
        assert not RawLoader.is_raw("photo.txt")

    def test_all_raw_extensions_lowercase(self) -> None:
        """所有 RAW 扩展名应为小写."""
        for ext in ALL_RAW_EXTENSIONS:
            assert ext == ext.lower(), f"{ext} 未小写"

    def test_get_supported_raw_formats(self) -> None:
        formats = RawLoader.get_supported_raw_formats()
        assert len(formats) >= 6
        assert "RAW_CR2" in formats
        assert "RAW_DNG" in formats

    def test_load_preview_no_rawpy(self) -> None:
        """无 rawpy 时应抛出 RawLoadError."""
        if not RawLoader.is_available():
            with pytest.raises(RawLoadError):
                RawLoader.load_preview("nonexistent.cr2")
        else:
            pytest.skip("rawpy 已安装，跳过此测试")

    def test_load_full_no_rawpy(self) -> None:
        if not RawLoader.is_available():
            with pytest.raises(RawLoadError):
                RawLoader.load_full("nonexistent.cr2")
        else:
            pytest.skip("rawpy 已安装，跳过此测试")

    def test_get_info_no_rawpy(self) -> None:
        if not RawLoader.is_available():
            with pytest.raises(RawLoadError):
                RawLoader.get_info("nonexistent.cr2")
        else:
            pytest.skip("rawpy 已安装，跳过此测试")

    def test_load_no_rawpy(self) -> None:
        if not RawLoader.is_available():
            with pytest.raises(RawLoadError):
                RawLoader.load("nonexistent.cr2")
        else:
            pytest.skip("rawpy 已安装，跳过此测试")


# ========== 批处理测试 ==========


class TestBatchProcessor:
    """批处理测试."""

    def test_convert_single(self, tmp_path: Path) -> None:
        """单文件格式转换."""
        # 创建测试图片
        src = tmp_path / "test.png"
        Image.new("RGB", (10, 10), (255, 0, 0)).save(src)
        out = tmp_path / "output"
        out.mkdir()

        result = BatchProcessor.convert(
            [src], out, "JPEG"
        )
        assert result.total == 1
        assert result.succeeded == 1
        assert result.failed == 0
        assert (out / "test.jpg").exists()

    def test_convert_multiple(self, tmp_path: Path) -> None:
        """多文件格式转换."""
        out = tmp_path / "output"
        out.mkdir()

        files = []
        for i in range(3):
            f = tmp_path / f"test_{i}.png"
            Image.new("RGB", (5, 5), (i * 50, 0, 0)).save(f)
            files.append(f)

        result = BatchProcessor.convert(files, out, "WEBP")
        assert result.total == 3
        assert result.succeeded == 3
        for i in range(3):
            assert (out / f"test_{i}.webp").exists()

    def test_resize_with_aspect(self, tmp_path: Path) -> None:
        """调整大小（保持宽高比）."""
        src = tmp_path / "test.png"
        Image.new("RGB", (200, 100), (0, 255, 0)).save(src)
        out = tmp_path / "output"
        out.mkdir()

        result = BatchProcessor.resize(
            [src], out, (50, 50), keep_aspect=True
        )
        assert result.succeeded == 1
        # 验证保持宽高比
        with Image.open(out / "test.png") as img:
            w, h = img.size
            assert w <= 50
            assert h <= 50
            assert w / h == 2.0  # 宽高比应保持不变

    def test_resize_exact(self, tmp_path: Path) -> None:
        """调整大小（精确尺寸）."""
        src = tmp_path / "test.png"
        Image.new("RGB", (200, 100), (0, 0, 255)).save(src)
        out = tmp_path / "output"
        out.mkdir()

        result = BatchProcessor.resize(
            [src], out, (50, 50), keep_aspect=False
        )
        assert result.succeeded == 1
        with Image.open(out / "test.png") as img:
            assert img.size == (50, 50)

    def test_rename(self, tmp_path: Path) -> None:
        """批量重命名."""
        files = []
        for i in range(3):
            f = tmp_path / f"photo_{i}.jpg"
            f.write_text("test")
            files.append(f)

        result = BatchProcessor.rename(
            files, "img_{n:03d}", start_number=1
        )
        assert result.succeeded == 3
        assert (tmp_path / "img_001.jpg").exists()
        assert (tmp_path / "img_002.jpg").exists()
        assert (tmp_path / "img_003.jpg").exists()
        # 旧文件名不应存在
        assert not (tmp_path / "photo_0.jpg").exists()

    def test_rename_dry_run(self, tmp_path: Path) -> None:
        """重命名预览（不实际执行）."""
        files = []
        for i in range(2):
            f = tmp_path / f"img_{i}.jpg"
            f.write_text("test")
            files.append(f)

        result = BatchProcessor.rename(
            files, "new_{n:03d}", start_number=1, dry_run=True
        )
        assert result.succeeded == 2
        # 文件名不应被修改
        assert (tmp_path / "img_0.jpg").exists()
        assert (tmp_path / "img_1.jpg").exists()

    def test_convert_with_progress(self, tmp_path: Path) -> None:
        """带进度回调的转换."""
        src = tmp_path / "test.png"
        Image.new("RGB", (10, 10), (255, 0, 0)).save(src)
        out = tmp_path / "output"
        out.mkdir()

        progress_calls = []

        def progress(current, total, name):
            progress_calls.append((current, total, name))

        BatchProcessor.convert(
            [src], out, "JPEG", progress=progress
        )
        assert len(progress_calls) == 1
        assert progress_calls[0][0] == 1
        assert progress_calls[0][1] == 1

    def test_convert_invalid_format(self, tmp_path: Path) -> None:
        """无效格式应报告失败."""
        src = tmp_path / "test.png"
        Image.new("RGB", (10, 10), (255, 0, 0)).save(src)
        out = tmp_path / "output"
        out.mkdir()

        # 使用不存在的格式
        result = BatchProcessor.convert(
            [src], out, "UNKNOWN"
        )
        assert result.total == 1
        assert result.failed == 1


# ========== 插件系统测试 ==========


class TestPluginSystem:
    """插件发现与加载测试."""

    def test_discover_formats(self) -> None:
        """发现格式插件."""
        plugins = discover_plugins()
        assert "format" in plugins
        assert "filter" in plugins

    def test_example_plugin_loaded(self) -> None:
        """示例插件应被自动发现."""
        plugins = discover_plugins()
        format_names = [p.name() for p in plugins["format"]]
        filter_names = [p.name() for p in plugins["filter"]]
        assert "Example Image Format" in format_names
        assert "Vintage" in filter_names

    def test_example_plugin_extensions(self) -> None:
        """格式插件的扩展名."""
        plugins = discover_plugins()
        for p in plugins["format"]:
            if p.name() == "Example Image Format":
                assert ".example" in p.extensions()
                return
        pytest.fail("未找到 ExampleFormatPlugin")

    def test_discover_plugin_counts(self) -> None:
        """至少发现示例插件."""
        plugins = discover_plugins()
        assert len(plugins["format"]) >= 1
        assert len(plugins["filter"]) >= 1

    def test_discover_invalid_dir(self, tmp_path: Path) -> None:
        """无效的插件目录."""
        plugins = discover_plugins(tmp_path / "nonexistent")
        assert plugins == {"format": [], "filter": []}
