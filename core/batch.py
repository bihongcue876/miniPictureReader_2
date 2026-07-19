"""批处理模块 - 批量格式转换、调整大小、重命名."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence
from dataclasses import dataclass, field

from PIL import Image

from core.loader import ALL_EXTENSIONS


@dataclass
class BatchResult:
    """单文件批处理结果."""

    path: Path
    success: bool
    error: str | None = None


@dataclass
class BatchSummary:
    """批处理汇总."""

    total: int
    succeeded: int
    failed: int
    results: list[BatchResult] = field(default_factory=list)


ProgressCallback = Callable[[int, int, str], None]
"""进度回调: (current, total, filename)"""


class BatchProcessor:
    """批处理器."""

    @staticmethod
    def convert(
        files: Sequence[str | Path],
        output_dir: str | Path,
        target_format: str,
        progress: ProgressCallback | None = None,
    ) -> BatchSummary:
        """批量格式转换.

        Args:
            files: 源文件列表
            output_dir: 输出目录
            target_format: 目标格式 (JPEG, PNG, BMP, TIFF, WEBP)
            progress: 进度回调

        Returns:
            处理结果汇总
        """
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        results: list[BatchResult] = []
        fmt_map = {
            "JPEG": ".jpg", "PNG": ".png", "BMP": ".bmp",
            "TIFF": ".tif", "WEBP": ".webp",
        }
        ext = fmt_map.get(target_format.upper(), f".{target_format.lower()}")

        for i, file in enumerate(files):
            src = Path(file)
            name = src.stem + ext
            dst = output / name

            if progress:
                progress(i + 1, len(list(files)), src.name)

            try:
                with Image.open(src) as img:
                    save_img = img
                    if target_format.upper() == "JPEG":
                        save_img = img.convert("RGB")
                    save_img.save(dst, format=target_format.upper())
                results.append(BatchResult(path=dst, success=True))
            except Exception as e:
                results.append(
                    BatchResult(path=dst, success=False, error=str(e))
                )

        return BatchSummary(
            total=len(results),
            succeeded=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
            results=results,
        )

    @staticmethod
    def resize(
        files: Sequence[str | Path],
        output_dir: str | Path,
        size: tuple[int, int],
        keep_aspect: bool = True,
        progress: ProgressCallback | None = None,
    ) -> BatchSummary:
        """批量调整大小.

        Args:
            files: 源文件列表
            output_dir: 输出目录
            size: (width, height)
            keep_aspect: 是否保持宽高比
            progress: 进度回调

        Returns:
            处理结果汇总
        """
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        results: list[BatchResult] = []

        for i, file in enumerate(files):
            src = Path(file)
            dst = output / src.name

            if progress:
                progress(i + 1, len(list(files)), src.name)

            try:
                with Image.open(src) as img:
                    if keep_aspect:
                        img.thumbnail(size, Image.LANCZOS)
                    else:
                        img = img.resize(size, Image.LANCZOS)
                    img.save(dst)
                results.append(BatchResult(path=dst, success=True))
            except Exception as e:
                results.append(
                    BatchResult(path=dst, success=False, error=str(e))
                )

        return BatchSummary(
            total=len(results),
            succeeded=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
            results=results,
        )

    @staticmethod
    def rename(
        files: Sequence[str | Path],
        pattern: str,
        start_number: int = 1,
        dry_run: bool = False,
        progress: ProgressCallback | None = None,
    ) -> BatchSummary:
        """批量重命名.

        Args:
            files: 源文件列表（按此顺序重命名）
            pattern: 命名模板，如 "photo_{n:03d}" 中的 {n:03d} 表示序号
            start_number: 起始编号
            dry_run: 仅预览，不实际执行
            progress: 进度回调

        Returns:
            处理结果汇总
        """
        results: list[BatchResult] = []

        for i, file in enumerate(files):
            src = Path(file)
            num = start_number + i
            new_name = pattern.format(n=num, i=i)
            # 保留原扩展名
            new_name += src.suffix
            dst = src.with_name(new_name)

            if progress:
                progress(i + 1, len(list(files)), src.name)

            if dry_run:
                results.append(BatchResult(path=dst, success=True))
            else:
                try:
                    src.rename(dst)
                    results.append(BatchResult(path=dst, success=True))
                except Exception as e:
                    results.append(
                        BatchResult(path=src, success=False, error=str(e))
                    )

        return BatchSummary(
            total=len(results),
            succeeded=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
            results=results,
        )
