"""EXIF 处理模块 - 读取/写入/清除图片 EXIF 元数据."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import piexif
from PIL import Image

# ---------- EXIF 字段分类 ----------

_EXIF_CATEGORIES: dict[str, str] = {
    # 基本信息
    "ImageMake": "基本信息",
    "ImageModel": "基本信息",
    "ImageDateTime": "基本信息",
    "ImageSoftware": "基本信息",
    "ImageArtist": "基本信息",
    "ImageCopyright": "基本信息",
    "ImageImageDescription": "基本信息",
    # 拍摄参数
    "ExifExposureTime": "拍摄参数",
    "ExifFNumber": "拍摄参数",
    "ExifISOSpeedRatings": "拍摄参数",
    "ExifFocalLength": "拍摄参数",
    "ExifFocalLengthIn35mmFilm": "拍摄参数",
    "ExifExposureBiasValue": "拍摄参数",
    "ExifMeteringMode": "拍摄参数",
    "ExifFlash": "拍摄参数",
    "ExifWhiteBalance": "拍摄参数",
    "ExifDigitalZoomRatio": "拍摄参数",
    # 镜头信息
    "ExifLensMake": "拍摄参数",
    "ExifLensModel": "拍摄参数",
    # GPS
    "GPSGPSLatitudeRef": "GPS",
    "GPSGPSLatitude": "GPS",
    "GPSGPSLongitudeRef": "GPS",
    "GPSGPSLongitude": "GPS",
    "GPSGPSAltitudeRef": "GPS",
    "GPSGPSAltitude": "GPS",
}

# 可编辑字段白名单
_EDITABLE_FIELDS: set[str] = {
    "ImageImageDescription",
    "ImageArtist",
    "ImageCopyright",
    "ImageSoftware",
    "ExifWhiteBalance",
}


def _exif_key_to_label(key: str) -> str:
    """将 EXIF 键名转换为人类可读标签."""
    labels = {
        "ImageMake": "相机厂商",
        "ImageModel": "相机型号",
        "ImageDateTime": "拍摄时间",
        "ImageSoftware": "软件",
        "ImageArtist": "作者",
        "ImageCopyright": "版权信息",
        "ImageImageDescription": "图片描述",
        "ExifExposureTime": "曝光时间",
        "ExifFNumber": "光圈值",
        "ExifISOSpeedRatings": "ISO 感光度",
        "ExifFocalLength": "焦距",
        "ExifFocalLengthIn35mmFilm": "等效焦距(35mm)",
        "ExifExposureBiasValue": "曝光补偿",
        "ExifMeteringMode": "测光模式",
        "ExifFlash": "闪光灯",
        "ExifWhiteBalance": "白平衡",
        "ExifDigitalZoomRatio": "数码变焦",
        "ExifLensMake": "镜头厂商",
        "ExifLensModel": "镜头型号",
        "GPSGPSLatitudeRef": "纬度参考",
        "GPSGPSLatitude": "纬度",
        "GPSGPSLongitudeRef": "经度参考",
        "GPSGPSLongitude": "经度",
        "GPSGPSAltitudeRef": "海拔参考",
        "GPSGPSAltitude": "海拔",
    }
    return labels.get(key, key)


def _format_exif_value(value: Any) -> str:
    """格式化 EXIF 值为可读字符串."""
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="replace")
        except Exception:
            return repr(value)
    if isinstance(value, tuple):
        # 处理分数（如光圈、快门速度）
        if len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], int):
            if value[1] == 1:
                return str(value[0])
            return f"{value[0]}/{value[1]}"
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return value.strip()
    return str(value)


def _convert_rational(value: Any) -> tuple[int, int] | Any:
    """转换分数值为 (numerator, denominator) 元组."""
    if isinstance(value, tuple) and len(value) == 2:
        return value
    if isinstance(value, int):
        return (value, 1)
    return value


class ExifHandler:
    """EXIF 数据处理器."""

    @staticmethod
    def read_exif(path: str | Path) -> dict[str, dict[str, tuple[str, str, bool]]]:
        """读取 EXIF 数据，返回分类后的结构化数据.

        Returns:
            { "基本信息": { "label": ("key", "value", is_editable) }, ... }
        """
        result: dict[str, dict[str, tuple[str, str, bool]]] = {
            "基本信息": {},
            "拍摄参数": {},
            "GPS": {},
            "其他": {},
        }

        try:
            exif_data = piexif.load(str(path))
        except Exception:
            return result

        # 处理 IFD 各段
        for ifd_name, ifd_data in exif_data.items():
            if ifd_name == "thumbnail":
                continue
            if not isinstance(ifd_data, dict):
                continue

            for tag, value in ifd_data.items():
                # 构造完整键名
                if ifd_name == "0th":
                    key = f"Image{piexif.TAGS[ifd_name].get(tag, {}).get('name', str(tag))}"
                elif ifd_name == "Exif":
                    key = f"Exif{piexif.TAGS[ifd_name].get(tag, {}).get('name', str(tag))}"
                elif ifd_name == "GPS":
                    key = f"GPS{piexif.TAGS[ifd_name].get(tag, {}).get('name', str(tag))}"
                elif ifd_name == "1st":
                    key = f"Image{piexif.TAGS[ifd_name].get(tag, {}).get('name', str(tag))}"
                else:
                    continue

                category = _EXIF_CATEGORIES.get(key, "其他")
                label = _exif_key_to_label(key)
                formatted = _format_exif_value(value)
                editable = key in _EDITABLE_FIELDS

                if category not in result:
                    result[category] = {}

                # 避免重复键
                if label not in result[category]:
                    result[category][label] = (key, formatted, editable)
                else:
                    # 放入"其他"
                    result.setdefault("其他", {})
                    result["其他"][f"{label} ({key})"] = (key, formatted, editable)

        return result

    @staticmethod
    def write_exif(path: str | Path, data: dict[str, str]) -> bool:
        """写入 EXIF 字段.

        Args:
            path: 图片路径
            data: { "ImageCopyright": "value", ... } 格式的字段字典

        Returns:
            是否成功
        """
        try:
            exif_data = piexif.load(str(path))
        except Exception:
            return False

        # 键名 → piexif IFD 常量 映射
        _FIELD_MAP: dict[str, tuple[str, int]] = {
            "ImageImageDescription": ("0th", piexif.ImageIFD.ImageDescription),
            "ImageArtist": ("0th", piexif.ImageIFD.Artist),
            "ImageCopyright": ("0th", piexif.ImageIFD.Copyright),
            "ImageSoftware": ("0th", piexif.ImageIFD.Software),
            "ImageMake": ("0th", piexif.ImageIFD.Make),
            "ImageModel": ("0th", piexif.ImageIFD.Model),
            "ImageDateTime": ("0th", piexif.ImageIFD.DateTime),
        }

        for key, value in data.items():
            mapping = _FIELD_MAP.get(key)
            if mapping is not None:
                ifd_name, tag = mapping
                exif_data[ifd_name][tag] = value.encode("utf-8")

        try:
            exif_bytes = piexif.dump(exif_data)
            piexif.insert(exif_bytes, str(path))
            return True
        except Exception:
            return False

    @staticmethod
    def clear_exif(path: str | Path) -> bool:
        """清除图片所有 EXIF 数据."""
        try:
            piexif.remove(str(path))
            return True
        except Exception:
            return False

    @staticmethod
    def get_gps_coordinates(
        path: str | Path,
    ) -> tuple[float, float] | None:
        """提取 GPS 坐标.

        Returns:
            (latitude, longitude) 或 None
        """
        try:
            exif_data = piexif.load(str(path))
        except Exception:
            return None

        gps = exif_data.get("GPS")
        if not gps:
            return None

        lat_ref = gps.get(piexif.GPSIFD.GPSLatitudeRef)
        lat_data = gps.get(piexif.GPSIFD.GPSLatitude)
        lon_ref = gps.get(piexif.GPSIFD.GPSLongitudeRef)
        lon_data = gps.get(piexif.GPSIFD.GPSLongitude)

        if not all([lat_ref, lat_data, lon_ref, lon_data]):
            return None

        def _dms_to_decimal(
            dms: tuple[int, int] | tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
            ref: bytes,
        ) -> float:
            """度分秒 → 十进制."""
            if isinstance(dms[0], tuple):
                # ( (d,n), (m,n), (s,n) ) 格式
                d = dms[0][0] / dms[0][1] if dms[0][1] != 0 else 0
                m = dms[1][0] / dms[1][1] if dms[1][1] != 0 else 0
                s = dms[2][0] / dms[2][1] if dms[2][1] != 0 else 0
            else:
                d = float(dms[0])
                m = float(dms[1])
                s = float(dms[2])

            decimal = d + m / 60.0 + s / 3600.0
            if ref in (b"S", b"W"):
                decimal = -decimal
            return decimal

        try:
            lat = _dms_to_decimal(lat_data, lat_ref)
            lon = _dms_to_decimal(lon_data, lon_ref)
            return (lat, lon)
        except Exception:
            return None
