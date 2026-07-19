# PictureReader

轻量级跨平台图片查看与管理工具，支持常见图片格式及相机 RAW 格式的浏览、EXIF 元数据处理、基础编辑功能。

- 项目开发方式：采用软件工程一般流程，集成单中心多结构的应用，使用平台TRAE IDE SOLO进行基本开发。
- 本项目是开发演示的结果。

## 特性

### Phase 1 — 核心看图 (MVP) ✅
- **目录导航** — 目录树 + 文件列表，快速浏览文件夹内图片
- **格式筛选** — 按格式预设筛选图片（JPEG / PNG / WEBP / 位图等）
- **图片渲染** — 支持 JPEG、PNG、GIF、BMP、TIFF、WEBP、ICO、PPM
- **平滑缩放** — 滚轮以鼠标位置为中心缩放，快捷键 `Ctrl++` / `Ctrl+-` / `Ctrl+0`
- **拖拽平移** — 图片大于窗口时拖拽平移，手型光标
- **图片导航** — 方向键上一张/下一张、Home/End 首末跳转、循环导航

### Phase 2 — EXIF 与基础编辑 ✅
- **EXIF 查看** — 分类展示基本信息、拍摄参数、GPS 坐标
- **EXIF 编辑** — 修改日期时间、描述、版权等字段，支持删除全部 EXIF
- **基础编辑** — 旋转（90°/180°/270°）、翻转（水平/垂直）、裁剪
- **撤销/重做** — 当前会话内多步撤销/重做

### Phase 3 — 增强功能 ✅
- **图像调整** — 亮度、对比度、饱和度、色相滑块，实时预览 + 自动优化
- **直方图** — QPainter 绘制，辅助色阶调整
- **缩略图网格** — 网格浏览 + LRU 缓存 + 大小可调
- **幻灯片播放** — 全屏模式，间隔/顺序/随机可配，过渡动画
- **文件管理** — 重命名、删除（回收站）、复制/移动、在文件管理器中显示

### Phase 4 — 高级功能 ✅
- **RAW 支持** — CR2 / NEF / ARW / RAF / DNG 解码（依赖 RawPy）
- **批处理** — 批量格式转换、调整大小、重命名，进度条反馈
- **插件接口** — 格式解析器接口 + 图像滤镜接口 + 热加载机制
- **示例插件** — `plugins/example_plugin.py`

## 快速开始

### 环境要求

- Python 3.10+
- 操作系统：Windows 10+ / macOS 12+ / Linux (X11/Wayland)

### 安装

```bash
# 克隆仓库
git clone https://github.com/your/picture-reader.git
cd picture-reader

# 创建虚拟环境（推荐使用 uv 或 venv）
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 如需 RAW 格式支持，额外安装
pip install -r requirements-raw.txt

# 开发模式安装
pip install -e .[dev]

# 或直接运行
python main.py
```

## 项目结构

```
pictureReader2/
├── core/                    # 核心逻辑层（零 GUI 依赖）
│   ├── loader.py            # 图片加载、格式检测、缩略图
│   ├── exif_handler.py      # EXIF 读写、GPS 解析
│   ├── editor.py            # 图像变换与调整
│   ├── filters.py           # 格式筛选逻辑
│   ├── raw_loader.py        # RAW 格式解码
│   ├── batch.py             # 批处理
│   └── interfaces.py        # 插件接口定义
├── ui/                      # GUI 界面层（PySide6）
│   ├── app.py               # 主窗口、菜单栏、快捷键
│   ├── viewer.py            # 图片画布、缩放/平移
│   ├── file_panel.py        # 目录树 + 文件列表
│   ├── edit_panel.py        # 编辑工具栏
│   ├── exif_panel.py        # EXIF 信息表格
│   ├── thumb_view.py        # 缩略图网格
│   ├── slideshow.py         # 全屏幻灯片
│   ├── adjust_panel.py      # 图像调整滑块
│   └── batch_dialog.py      # 批处理对话框
├── plugins/                 # 插件目录
│   └── example_plugin.py    # 示例插件
├── tests/                   # 测试
│   ├── conftest.py          # pytest fixtures
│   ├── test_loader.py
│   ├── test_exif.py
│   ├── test_editor.py
│   ├── test_filters.py
│   └── ...
├── main.py                  # 程序入口
├── requirements.txt         # 核心依赖
├── requirements-raw.txt     # RAW 可选依赖
├── pyproject.toml           # 项目元数据
└── spec.md                  # 需求规约
```

## 测试

```bash
pytest                    # 运行全部测试
pytest -v                 # 详细输出
pytest tests/test_loader.py  # 运行单个测试文件
pytest --cov=core         # 带覆盖率报告
```

## 构建

```bash
# 使用 PyInstaller 打包
pyinstaller --name PictureReader --windowed --onefile main.py
```

## 许可

本项目采用 MIT 许可协议。
