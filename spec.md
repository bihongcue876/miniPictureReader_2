# PictureReader — 软件需求规约 (SRS)

> 版本: 1.0  
> 最后更新: 2026-07-19  
> 状态: 草稿

---

## 1. 项目概述

### 1.1 产品定位
轻量级跨平台图片查看与管理工具，支持常见图片格式及相机 RAW 格式的浏览、EXIF 元数据处理、基础编辑功能。

### 1.2 设计目标
- **轻量级** — 核心依赖精简，RAW 等高级功能作为可选扩展
- **模块化** — 核心逻辑层与 GUI 层分离，支持 CLI 调用和第三方集成
- **可扩展** — 预留插件接口，支持格式解析器和编辑功能扩展
- **MVP 驱动** — 分阶段交付，每阶段产出可用的可交付物

### 1.3 技术栈
- 语言: Python 3.10+
- GUI: PySide6 (Qt for Python)
- 图像处理: Pillow, RawPy (可选)
- 打包: PyInstaller / Nuitka

---

## 2. 功能需求

### 2.1 功能全景图

```
Phase 1 (MVP)          Phase 2              Phase 3              Phase 4
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ 基础图片浏览   │   │ EXIF 读写     │   │ 图像调整      │   │ RAW 支持      │
│ 目录导航      │   │ 旋转/翻转/裁剪 │   │ 缩略图网格    │   │ 批处理        │
│ 格式筛选      │   │ 编辑工具栏    │   │ 幻灯片播放    │   │ 插件接口      │
│ 缩放/平移     │   │              │   │ 文件管理操作   │   │              │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

### 2.2 Phase 1 — 核心看图 (MVP)

#### FR-01: 目录导航与文件浏览
- 用户可通过目录树选择文件夹
- 文件列表显示文件夹内所有支持格式的图片
- 支持自定义格式筛选（如仅显示 JPEG、仅显示 RAW 等）
- 支持文件排序（名称、修改日期、大小）

#### FR-02: 图片渲染与查看
- 支持以下格式解码与渲染：
  - 常见格式: JPEG, PNG, GIF (静态), BMP, TIFF, WEBP, ICO, PPM
  - 当前 Phase 暂不支持 RAW（Phase 4 添加）
- 图片自适应窗口大小显示
- 支持 1:1 原始大小显示
- 图片平滑缩放，无锯齿

#### FR-03: 缩放与平移
- 滚轮缩放（以鼠标位置为中心）
- 快捷键缩放: `Ctrl++` 放大, `Ctrl+-` 缩小, `Ctrl+0` 适应窗口
- 缩放比例显示在状态栏
- 图片大于窗口时，支持拖拽平移
- 平移时显示手型光标

#### FR-04: 图片导航
- 上一张/下一张切换（快捷键: 方向键左/右）
- 首张/末张快捷跳转（快捷键: Home/End）
- 导航到上一张/下一张时保持缩放比例
- 循环导航（末张后回到首张）

#### FR-05: 格式筛选
- 下拉筛选器选择要显示的格式组合
- 预设筛选: 所有图片、仅位图、仅JPEG、仅PNG、仅WEBP、自定义
- 筛选器状态持久化（会话期间）

### 2.3 Phase 2 — EXIF 与基础编辑

#### FR-06: EXIF 信息查看
- 在侧面板显示当前图片的 EXIF 元数据
- 分类展示: 基本信息（厂商、型号、时间）、拍摄参数（光圈、快门、ISO、焦距）、GPS 位置
- GPS 坐标可点击（如需后续集成地图）

#### FR-07: EXIF 编辑
- 支持编辑部分 EXIF 字段（如：日期时间、描述、版权信息）
- 支持删除全部 EXIF 信息（隐私保护）
- 编辑后保存到文件（非破坏性，仅修改元数据）

#### FR-08: 基础编辑操作
- 旋转: 左旋 90°、右旋 90°、180°
- 翻转: 水平翻转、垂直翻转
- 裁剪: 鼠标拖拽选择矩形区域，确认裁剪
- 所有编辑操作支持撤销/重做（仅当前会话）

### 2.4 Phase 3 — 增强功能

#### FR-09: 图像调整
- 亮度/对比度滑块调节
- 饱和度/色相调节
- 色阶调整（直方图辅助）
- 一键自动优化

#### FR-10: 缩略图模式
- 网格状缩略图浏览
- 缩略图大小可调（小/中/大）
- 缩略图缓存加速

#### FR-11: 幻灯片播放
- 全屏幻灯片模式
- 播放间隔可调（1-60秒）
- 随机/顺序播放模式
- 过渡动画（淡入淡出）

#### FR-12: 文件管理
- 重命名当前图片
- 删除（移动至回收站）
- 复制/移动到其他目录
- 在文件管理器中显示

### 2.5 Phase 4 — 高级功能

#### FR-13: RAW 格式支持
- 支持主流相机 RAW 格式: CR2 (Canon), NEF (Nikon), ARW (Sony), RAF (Fujifilm), DNG (Adobe)
- RAW 解码依赖 RawPy (libraw)
- RAW 预览显示嵌入式 JPEG 预览图
- 支持 RAW 文件的基本曝光调整

#### FR-14: 批处理
- 批量格式转换（支持目标格式: JPEG, PNG, TIFF, WEBP）
- 批量调整大小（按百分比或固定尺寸）
- 批量重命名（模板命名规则）
- 处理进度条显示

#### FR-15: 插件接口
- 定义标准的格式解析器接口
- 定义标准的图像滤镜/编辑接口
- 插件热加载机制
- 示例插件模板

---

## 3. 非功能需求

### NFR-01: 性能
- 首屏加载时间 < 500ms（本地图片，JPEG 5MB 以内）
- 缩略图生成时间 < 200ms/张
- 缩放操作响应时间 < 100ms
- 内存占用: 同时打开 10 张 20MB 图片时内存 < 500MB

### NFR-02: 可用性
- 全键盘快捷键操作
- 鼠标拖拽/滚轮交互
- 状态栏信息提示
- 操作错误有明确的用户反馈

### NFR-03: 兼容性
- 操作系统: Windows 10+ / macOS 12+ / Linux (X11/Wayland)
- Python 3.10+
- 支持高 DPI 显示（Retina 屏幕）

### NFR-04: 可维护性
- 模块化分层架构
- 核心逻辑单元测试覆盖率 > 80%
- 代码遵循 PEP 8
- 类型注解覆盖率 > 90%

---

## 4. 架构设计

### 4.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                        UI Layer (PySide6)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ MainWin  │ │ Viewer   │ │FilePanel │ │ EditPanel      │   │
│  │  (app)   │ │ (canvas) │ │(tree+list)│ │(tools)         │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───────┬────────┘   │
│       │            │            │                │            │
├───────┴────────────┴────────────┴────────────────┴────────────┤
│                      Core Service Layer                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ImageLoader│ │ExifHandler│ │ Editor   │ │ FormatFilter   │   │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘   │
│         │              │            │                          │
├─────────┴──────────────┴────────────┴──────────────────────────┤
│                   Infrastructure Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ Pillow   │ │ RawPy    │ │ numpy    │ │ File System    │   │
│  │ (core)   │ │ (plugin) │ │ (processing)│                │   │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 模块职责

#### core/ 层（纯 Python，零 GUI 依赖）

| 模块 | 职责 | 关键类/函数 |
|------|------|------------|
| `loader.py` | 图片加载、格式检测、缩略图生成 | `ImageLoader`, `load_image()`, `get_thumbnail()` |
| `exif_handler.py` | EXIF 读写、GPS 解析 | `ExifHandler`, `read_exif()`, `write_exif()`, `clear_exif()` |
| `editor.py` | 图像变换与调整 | `ImageEditor`, `rotate()`, `flip()`, `crop()`, `adjust()` |
| `filters.py` | 格式筛选逻辑 | `FormatFilter`, `FilterPreset`, `match()` |
| `raw_loader.py` | RAW 格式解码 | `RawLoader`, `load_raw()`, `get_preview()` |
| `batch.py` | 批处理任务 | `BatchProcessor`, `convert()`, `resize()`, `rename()` |

#### ui/ 层

| 模块 | 职责 |
|------|------|
| `app.py` | 主窗口、菜单栏、状态栏、快捷键绑定 |
| `viewer.py` | 图片画布（QLabel/QGraphicsView）、缩放/平移 |
| `file_panel.py` | 目录树 (QTreeView) + 文件列表 (QListView/QTableView) |
| `edit_panel.py` | 编辑工具栏 + 参数滑块 |
| `exif_panel.py` | EXIF 信息表格 (QTableWidget) |
| `thumb_view.py` | 缩略图网格浏览 |
| `slideshow.py` | 全屏幻灯片窗口 |

### 4.3 关键数据结构

```python
@dataclass
class ImageInfo:
    path: Path
    format: str            # 如 "JPEG", "PNG", "RAW_CR2"
    size: tuple[int, int]  # 原始尺寸 (width, height)
    file_size: int         # 文件大小（字节）
    modified: datetime     # 修改时间
    exif: dict | None      # EXIF 数据（可选）

@dataclass
class FilterPreset:
    name: str              # 预设名称
    formats: list[str]     # 允许的格式列表
    is_custom: bool = False
```

---

## 5. 接口规约

### 5.1 core.ImageLoader

```python
class ImageLoader:
    def load(path: Path | str) -> ImageInfo
    def load_pixmap(path: Path | str, max_size: tuple | None = None) -> QPixmap
    def get_thumbnail(path: Path | str, size: tuple = (256, 256)) -> QPixmap
    def get_supported_formats() -> list[str]
    def is_supported(path: Path | str) -> bool
```

### 5.2 core.ExifHandler

```python
class ExifHandler:
    def read_exif(path: Path | str) -> dict
    def write_exif(path: Path | str, data: dict) -> bool
    def clear_exif(path: Path | str) -> bool
    def get_gps_coordinates(path: Path | str) -> tuple[float, float] | None
```

### 5.3 core.ImageEditor

```python
class ImageEditor:
    def __init__(self, image: PIL.Image):
    def rotate(self, angle: int) -> ImageEditor          # 90, 180, 270
    def flip(self, direction: str) -> ImageEditor         # "horizontal", "vertical"
    def crop(self, box: tuple[int,int,int,int]) -> ImageEditor
    def resize(self, size: tuple[int,int]) -> ImageEditor
    def adjust_brightness(self, factor: float) -> ImageEditor
    def adjust_contrast(self, factor: float) -> ImageEditor
    def adjust_saturation(self, factor: float) -> ImageEditor
    def undo(self) -> ImageEditor
    def redo(self) -> ImageEditor
    def save(self, path: Path | str, format: str | None = None) -> bool
```

---

## 6. 测试策略

### 6.1 单元测试（core 层）
- 使用 pytest
- `tests/test_loader.py` — 各种格式加载测试、异常路径测试
- `tests/test_exif.py` — EXIF 读写测试、GPS 解析测试
- `tests/test_editor.py` — 编辑操作正确性测试、撤销/重做测试
- `tests/test_filters.py` — 格式筛选逻辑测试
- `tests/test_raw.py` — RAW 解码测试（若安装 rawpy）

### 6.2 集成测试
- `tests/test_pipeline.py` — 加载→编辑→保存 完整链路
- `tests/test_file_ops.py` — 文件操作集成测试

### 6.3 GUI 测试
- 使用 pytest-qt / QTest
- 验证界面交互（按钮点击、快捷键、拖拽）
- 验证缩放/平移正确性
- 验证筛选器状态同步

### 6.4 测试覆盖率目标
- core 层: > 85%
- UI 层: > 60%
- 总体: > 75%

---

## 7. 项目目录结构

```
pictureReader2/
├── core/                    # 核心逻辑层
│   ├── __init__.py
│   ├── loader.py            # 图片加载
│   ├── exif_handler.py      # EXIF 处理
│   ├── editor.py            # 图像编辑
│   ├── filters.py           # 格式筛选
│   ├── raw_loader.py        # RAW 解码（可选）
│   ├── batch.py             # 批处理
│   └── interfaces.py        # 插件接口定义
├── ui/                      # GUI 界面层
│   ├── __init__.py
│   ├── app.py               # 主窗口
│   ├── viewer.py            # 图片查看组件
│   ├── file_panel.py        # 文件浏览面板
│   ├── edit_panel.py        # 编辑工具栏
│   ├── exif_panel.py        # EXIF 面板
│   ├── thumb_view.py        # 缩略图视图
│   ├── slideshow.py         # 幻灯片
│   └── resources/           # 图标/资源
│       └── icons/
├── plugins/                 # 插件目录
│   └── example_plugin.py    # 示例插件
├── tests/                   # 测试
│   ├── __init__.py
│   ├── conftest.py          # pytest fixtures
│   ├── test_loader.py
│   ├── test_exif.py
│   ├── test_editor.py
│   ├── test_filters.py
│   ├── test_raw.py
│   └── test_pipeline.py
├── main.py                  # 程序入口
├── requirements.txt         # 核心依赖
├── requirements-raw.txt     # RAW 可选依赖
├── spec.md                  # 本需求规约文件
├── checklist.md             # 开发检查清单
└── tasks.md                 # 任务分解计划
```
