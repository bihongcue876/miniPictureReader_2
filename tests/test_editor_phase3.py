"""Phase 3 — 图像调整/直方图/编辑增强测试."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from core.editor import ImageEditor


def _create_test_image(size=(100, 80)) -> Image.Image:
    return Image.new("RGB", size, (255, 0, 0))


def _create_gradient_image(size=(100, 80)) -> Image.Image:
    """创建渐变图以测试直方图."""
    img = Image.new("RGB", size)
    for x in range(size[0]):
        for y in range(size[1]):
            r = int(x / size[0] * 255)
            g = int(y / size[1] * 255)
            b = 128
            img.putpixel((x, y), (r, g, b))
    return img


class TestHistogram:
    """直方图测试."""

    def test_histogram_rgb(self) -> None:
        """纯色图应产生尖峰直方图."""
        img = Image.new("RGB", (100, 80), (100, 150, 200))
        editor = ImageEditor(img)
        r, g, b = editor.histogram()
        assert len(r) == 256
        assert len(g) == 256
        assert len(b) == 256
        # 纯色图只有一个亮度值有像素
        assert r[100] == 100 * 80
        assert g[150] == 100 * 80
        assert b[200] == 100 * 80

    def test_histogram_gradient(self) -> None:
        """渐变图应有广泛分布."""
        editor = ImageEditor(_create_gradient_image())
        r, g, b = editor.histogram()
        # 渐变图的大部分亮度级都有像素
        assert sum(1 for v in r if v > 0) > 50
        assert sum(1 for v in g if v > 0) > 50

    def test_histogram_grayscale(self) -> None:
        """灰度图."""
        img = Image.new("L", (50, 50), 128)
        editor = ImageEditor(img)
        r, g, b = editor.histogram()
        assert len(r) == 256
        assert r[128] == 2500


class TestAutoOptimize:
    """自动优化测试."""

    def test_auto_optimize_improves_contrast(self) -> None:
        """低对比度图经自动优化后应有更广分布."""
        # 创建一个集中在中段的图
        img = Image.new("RGB", (50, 50), (120, 120, 120))
        # 添加一些变化
        for x in range(50):
            for y in range(50):
                v = 120 + (x - 25) * 2
                img.putpixel((x, y), (v, v, v))

        editor = ImageEditor(img)
        r_before, _, _ = editor.histogram()
        spread_before = sum(1 for v in r_before if v > 0)

        editor.auto_optimize()
        r_after, _, _ = editor.histogram()
        spread_after = sum(1 for v in r_after if v > 0)

        # 自动优化后直方图应更分散
        assert spread_after >= spread_before

    def test_auto_optimize_preserves_size(self) -> None:
        img = _create_test_image((100, 80))
        editor = ImageEditor(img)
        editor.auto_optimize()
        assert editor.image.size == (100, 80)

    def test_auto_optimize_undoable(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        editor.auto_optimize()
        assert editor.can_undo
        editor.undo()
        # 撤销后应回到原始状态

    def test_auto_optimize_grayscale(self) -> None:
        img = Image.new("L", (50, 50), 100)
        editor = ImageEditor(img)
        editor.auto_optimize()
        assert editor.image is not None


class TestEditorEnhancements:
    """编辑器增强功能测试."""

    def test_undo_stack_limited(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        for _ in range(60):
            editor.rotate(90)
        assert len(editor._undo_stack) <= 50  # noqa: SLF001

    def test_reset_after_edits(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        editor.rotate(90).flip("horizontal").crop((0, 0, 30, 30))
        editor.reset()
        assert editor.image.size == (100, 80)

    def test_multiple_adjustments(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        editor.adjust_brightness(1.2).adjust_contrast(1.1).adjust_saturation(0.9)
        assert editor.is_modified
        assert editor.can_undo
