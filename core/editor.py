"""图像编辑模块 - 旋转、翻转、裁剪、调整及撤销/重做."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageEnhance


class ImageEditor:
    """图像编辑器 - 支持链式调用和撤销/重做."""

    def __init__(self, image: Image.Image) -> None:
        self._original = image.copy()
        self._current = image.copy()
        self._undo_stack: list[Image.Image] = []
        self._redo_stack: list[Image.Image] = []

    # ---------- 变换操作 ----------

    def rotate(self, angle: int) -> ImageEditor:
        """旋转图片 (90, 180, 270)."""
        self._save_state()
        if angle == 90:
            self._current = self._current.transpose(
                Image.Transpose.ROTATE_90
            )
        elif angle == 180:
            self._current = self._current.transpose(
                Image.Transpose.ROTATE_180
            )
        elif angle == 270:
            self._current = self._current.transpose(
                Image.Transpose.ROTATE_270
            )
        return self

    def flip(self, direction: str) -> ImageEditor:
        """翻转图片 ('horizontal' 或 'vertical')."""
        self._save_state()
        if direction == "horizontal":
            self._current = self._current.transpose(
                Image.Transpose.FLIP_LEFT_RIGHT
            )
        elif direction == "vertical":
            self._current = self._current.transpose(
                Image.Transpose.FLIP_TOP_BOTTOM
            )
        return self

    def crop(self, box: tuple[int, int, int, int]) -> ImageEditor:
        """裁剪图片.

        Args:
            box: (left, top, right, bottom) 像素坐标
        """
        self._save_state()
        self._current = self._current.crop(box)
        return self

    def resize(self, size: tuple[int, int]) -> ImageEditor:
        """调整图片大小."""
        self._save_state()
        self._current = self._current.resize(size, Image.LANCZOS)
        return self

    # ---------- 图像调整 ----------

    def adjust_brightness(self, factor: float) -> ImageEditor:
        """调整亮度 (0.0 ~ 2.0, 1.0 为原始)."""
        self._save_state()
        enhancer = ImageEnhance.Brightness(self._current)
        self._current = enhancer.enhance(factor)
        return self

    def adjust_contrast(self, factor: float) -> ImageEditor:
        """调整对比度 (0.0 ~ 2.0, 1.0 为原始)."""
        self._save_state()
        enhancer = ImageEnhance.Contrast(self._current)
        self._current = enhancer.enhance(factor)
        return self

    def adjust_saturation(self, factor: float) -> ImageEditor:
        """调整饱和度 (0.0 ~ 2.0, 1.0 为原始)."""
        self._save_state()
        enhancer = ImageEnhance.Color(self._current)
        self._current = enhancer.enhance(factor)
        return self

    # ---------- 直方图 ----------

    def histogram(self) -> tuple[list[int], list[int], list[int]]:
        """计算 RGB 各通道直方图.

        Returns:
            (r_hist, g_hist, b_hist) 各通道 256 级亮度分布
        """
        if self._current.mode == "RGB":
            r, g, b = self._current.split()
            return (
                r.histogram(),
                g.histogram(),
                b.histogram(),
            )
        # 灰度图转伪 RGB
        gray = self._current.convert("L")
        h = gray.histogram()
        return (h, h[:], h[:])

    def auto_optimize(self) -> ImageEditor:
        """自动优化：自动色阶（拉伸直方图到全范围）."""
        self._save_state()

        if self._current.mode != "RGB":
            self._current = self._current.convert("RGB")

        r, g, b = self._current.split()
        channels = []

        for ch in (r, g, b):
            hist = ch.histogram()
            total = sum(hist)

            # 去掉最低 0.5% 和最高 0.5% 的像素
            low_cut = int(total * 0.005)
            high_cut = int(total * 0.005)

            low_val = 0
            cum = 0
            for i, count in enumerate(hist):
                cum += count
                if cum > low_cut:
                    low_val = i
                    break

            high_val = 255
            cum = 0
            for i in range(255, -1, -1):
                cum += hist[i]
                if cum > high_cut:
                    high_val = i
                    break

            # 拉伸到 0-255
            if high_val > low_val:
                import numpy as np

                arr = np.array(ch, dtype=np.float32)
                arr = (arr - low_val) * (255.0 / (high_val - low_val))
                arr = np.clip(arr, 0, 255).astype(np.uint8)
                channels.append(Image.fromarray(arr, mode="L"))
            else:
                channels.append(ch)

        self._current = Image.merge("RGB", channels)
        return self

    # ---------- 撤销/重做 ----------

    def _save_state(self) -> None:
        """保存当前状态到撤销栈."""
        self._undo_stack.append(self._current.copy())
        # 新操作清空重做栈
        self._redo_stack.clear()
        # 限制撤销栈深度
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)

    def undo(self) -> ImageEditor:
        """撤销上一步操作."""
        if self._undo_stack:
            self._redo_stack.append(self._current.copy())
            self._current = self._undo_stack.pop()
        return self

    def redo(self) -> ImageEditor:
        """重做."""
        if self._redo_stack:
            self._undo_stack.append(self._current.copy())
            self._current = self._redo_stack.pop()
        return self

    def reset(self) -> ImageEditor:
        """重置为原始图片."""
        self._save_state()
        self._current = self._original.copy()
        return self

    # ---------- 保存 ----------

    def save(
        self,
        path: str | Path,
        format: str | None = None,
        **kwargs,
    ) -> bool:
        """保存图片到文件.

        Args:
            path: 保存路径
            format: 图片格式 (如 'JPEG', 'PNG')，None 则从扩展名推断
            **kwargs: 传递给 PIL.Image.save 的额外参数

        Returns:
            是否成功
        """
        try:
            # 转换为 RGB 以保存 JPEG
            if format and format.upper() == "JPEG":
                save_img = self._current.convert("RGB")
            else:
                save_img = self._current

            save_img.save(str(path), format=format, **kwargs)
            return True
        except Exception:
            return False

    def save_overwrite(self, path: str | Path) -> bool:
        """覆盖保存原文件."""
        p = Path(path)
        fmt = p.suffix.lstrip(".").upper()
        if fmt == "JPG":
            fmt = "JPEG"
        return self.save(p, format=fmt)

    # ---------- 属性 ----------

    @property
    def image(self) -> Image.Image:
        """获取当前图片."""
        return self._current.copy()

    @property
    def can_undo(self) -> bool:
        """是否可以撤销."""
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        """是否可以重做."""
        return len(self._redo_stack) > 0

    @property
    def is_modified(self) -> bool:
        """图片是否已被修改."""
        return bool(self._undo_stack)
