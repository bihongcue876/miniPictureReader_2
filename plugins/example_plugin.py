"""示例插件 - 演示 FormatPlugin 和 FilterPlugin 接口用法."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter

from core.interfaces import FormatPlugin, FilterPlugin


class ExampleFormatPlugin(FormatPlugin):
    """示例格式解析器 - 支持 .example 扩展名（实际是 PNG 伪装）."""

    @classmethod
    def extensions(cls) -> list[str]:
        return [".example"]

    @classmethod
    def name(cls) -> str:
        return "Example Image Format"

    def load(self, path: str | Path) -> Image.Image:
        """实际当作 PNG 加载."""
        return Image.open(path).convert("RGB")

    def can_load(self, path: str | Path) -> bool:
        p = Path(path)
        return p.suffix.lower() == ".example" and p.is_file()


class VintageFilterPlugin(FilterPlugin):
    """复古滤镜插件."""

    @classmethod
    def name(cls) -> str:
        return "Vintage"

    @classmethod
    def description(cls) -> str:
        return "应用复古色调和柔化效果"

    def apply(self, image: Image.Image, **params) -> Image.Image:
        """应用复古滤镜."""
        img = image.copy()

        # 柔化
        if params.get("blur", True):
            img = img.filter(ImageFilter.GaussianBlur(radius=1))

        # 转为 sepia 色调
        if img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size
        for x in range(w):
            for y in range(h):
                r, g, b = img.getpixel((x, y))
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                img.putpixel(
                    (x, y),
                    (min(tr, 255), min(tg, 255), min(tb, 255)),
                )

        return img
