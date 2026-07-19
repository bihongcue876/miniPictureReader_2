"""ImageEditor 单元测试."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from core.editor import ImageEditor


def _create_test_image(size=(100, 80)) -> Image.Image:
    return Image.new("RGB", size, (255, 0, 0))


class TestImageEditor:
    """图像编辑测试."""

    def test_initial_state(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        assert editor.image.size == (100, 80)
        assert not editor.is_modified
        assert not editor.can_undo
        assert not editor.can_redo

    def test_rotate_90(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img).rotate(90)
        assert editor.image.size == (80, 100)

    def test_rotate_180(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img).rotate(180)
        assert editor.image.size == (100, 80)

    def test_rotate_270(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img).rotate(270)
        assert editor.image.size == (80, 100)

    def test_flip_horizontal(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img).flip("horizontal")
        assert editor.image.size == (100, 80)

    def test_flip_vertical(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img).flip("vertical")
        assert editor.image.size == (100, 80)

    def test_crop(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img).crop((10, 10, 50, 50))
        assert editor.image.size == (40, 40)

    def test_resize(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img).resize((50, 50))
        assert editor.image.size == (50, 50)

    def test_chain_operations(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        editor.rotate(90).flip("horizontal").crop((0, 0, 50, 50))
        assert editor.image.size == (50, 50)
        assert editor.is_modified

    def test_brightness(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img).adjust_brightness(1.5)
        assert editor.image.size == (100, 80)

    def test_contrast(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img).adjust_contrast(1.5)
        assert editor.image.size == (100, 80)

    def test_saturation(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img).adjust_saturation(1.5)
        assert editor.image.size == (100, 80)

    def test_undo(self) -> None:
        img = _create_test_image((100, 80))
        editor = ImageEditor(img)
        editor.rotate(90)
        assert editor.image.size == (80, 100)
        editor.undo()
        assert editor.image.size == (100, 80)

    def test_undo_empty(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        editor.undo()  # 不应报错
        assert editor.image.size == (100, 80)

    def test_redo(self) -> None:
        img = _create_test_image((100, 80))
        editor = ImageEditor(img)
        editor.rotate(90)
        editor.undo()
        assert editor.image.size == (100, 80)
        editor.redo()
        assert editor.image.size == (80, 100)

    def test_redo_empty(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        editor.redo()  # 不应报错
        assert editor.image.size == (100, 80)

    def test_new_operation_clears_redo(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        editor.rotate(90)
        editor.undo()
        assert editor.can_redo
        editor.rotate(180)  # 新操作应清空重做栈
        assert not editor.can_redo

    def test_reset(self) -> None:
        img = _create_test_image((100, 80))
        editor = ImageEditor(img)
        editor.rotate(90).crop((0, 0, 50, 50))
        editor.reset()
        assert editor.image.size == (100, 80)

    def test_save_jpeg(self, tmp_path: Path) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        out = tmp_path / "out.jpg"
        ok = editor.save(out, format="JPEG")
        assert ok
        assert out.exists()

    def test_save_png(self, tmp_path: Path) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        out = tmp_path / "out.png"
        ok = editor.save(out, format="PNG")
        assert ok
        assert out.exists()

    def test_save_overwrite(self, tmp_path: Path) -> None:
        src = tmp_path / "src.jpg"
        img = _create_test_image()
        img.save(src)
        editor = ImageEditor(img)
        editor.rotate(90)
        ok = editor.save_overwrite(src)
        assert ok
        # 文件应存在且被覆盖
        assert src.exists()

    def test_is_modified(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        assert not editor.is_modified
        editor.rotate(90)
        assert editor.is_modified

    def test_can_undo_redo(self) -> None:
        img = _create_test_image()
        editor = ImageEditor(img)
        assert not editor.can_undo
        assert not editor.can_redo
        editor.rotate(90)
        assert editor.can_undo
        assert not editor.can_redo
        editor.undo()
        assert not editor.can_undo
        assert editor.can_redo
