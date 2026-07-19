# PictureReader — 开发检查清单

> 版本: 1.0  
> 说明: 按 Phase 和功能模块组织的开发与验证清单，每个条目完成后打勾。

---

## Phase 1 — 核心看图 (MVP)

### UI-01: 主窗口框架
- [ ] 创建 `ui/app.py` — MainWindow 继承 QMainWindow
- [ ] 菜单栏：文件、视图、帮助
- [ ] 状态栏：当前图片信息、缩放比例
- [ ] 窗口布局：左侧文件面板 + 中央查看区 + 右侧面板（预留）
- [ ] 高 DPI 支持 (`QApplication.setHighDpiScaleFactorRoundingPolicy`)

### UI-02: 文件浏览面板
- [ ] 目录树 (QTreeView + QFileSystemModel)
- [ ] 文件列表 (QListView)，显示图片缩略图 + 文件名
- [ ] 格式筛选下拉框
- [ ] 文件排序切换
- [ ] 双击文件打开图片

### UI-03: 图片查看器
- [ ] `ui/viewer.py` — 基于 QGraphicsView/QGraphicsScene
- [ ] 加载并显示图片（QPixmap）
- [ ] 自适应窗口大小（fit to window）
- [ ] 1:1 原始大小显示
- [ ] 平滑缩放（setTransformationAnchor: AnchorUnderMouse）

### UI-04: 缩放交互
- [ ] 滚轮缩放事件处理
- [ ] 快捷键: Ctrl++ / Ctrl+- / Ctrl+0
- [ ] 状态栏显示当前缩放百分比
- [ ] 缩放范围限制 (1% ~ 3200%)

### UI-05: 平移交互
- [ ] 图片大于视图时启用拖拽平移
- [ ] 手型光标切换
- [ ] 平移边界限制（不溢出视图边缘）

### UI-06: 图片导航
- [ ] 上一张/下一张按钮
- [ ] 快捷键: 方向键左/右
- [ ] Home/End 快捷跳转
- [ ] 循环导航
- [ ] 导航时保持缩放比例

### CORE-01: ImageLoader
- [ ] `core/loader.py` 实现
- [ ] 支持格式: JPEG, PNG, GIF, BMP, TIFF, WEBP, ICO, PPM
- [ ] 格式自动检测（基于文件头和扩展名）
- [ ] 图片信息读取 (ImageInfo dataclass)
- [ ] 缩略图生成
- [ ] 异常处理（损坏文件、不支持格式）

### CORE-02: FormatFilter
- [ ] `core/filters.py` 实现
- [ ] 预设筛选器定义
- [ ] 自定义格式组合筛选
- [ ] 文件扩展名匹配逻辑

### TEST-01: Phase 1 测试
- [ ] `tests/test_loader.py` — 格式加载测试
- [ ] `tests/test_filters.py` — 筛选逻辑测试
- [ ] `tests/conftest.py` — 测试夹具（样本图片生成）

---

## Phase 2 — EXIF 与基础编辑

### CORE-03: ExifHandler
- [ ] `core/exif_handler.py` 实现
- [ ] EXIF 数据读取 → 结构化 dict
- [ ] EXIF 字段分类展示（基本信息/拍摄参数/GPS）
- [ ] EXIF 写入（编辑特定字段）
- [ ] EXIF 清除
- [ ] GPS 坐标提取

### UI-07: EXIF 面板
- [ ] `ui/exif_panel.py` — QTableWidget 展示
- [ ] 分类折叠/展开
- [ ] 可编辑字段的交互
- [ ] 保存/清除按钮
- [ ] 无 EXIF 数据时的占位提示

### CORE-04: ImageEditor
- [ ] `core/editor.py` 实现
- [ ] 旋转（90°/180°/270°）
- [ ] 翻转（水平/垂直）
- [ ] 裁剪（矩形区域）
- [ ] 撤销/重做栈（Memento 模式）
- [ ] 保存到文件

### UI-08: 编辑工具栏
- [ ] `ui/edit_panel.py` — 工具栏布局
- [ ] 旋转/翻转按钮
- [ ] 裁剪模式切换（鼠标变为十字准星）
- [ ] 撤销/重做按钮
- [ ] 保存/另存为

### TEST-02: Phase 2 测试
- [ ] `tests/test_exif.py` — EXIF 读写测试
- [ ] `tests/test_editor.py` — 编辑操作测试
- [ ] 撤销/重做功能测试

---

## Phase 3 — 增强功能

### CORE-05: 图像调整
- [ ] 亮度/对比度调整
- [ ] 饱和度/色相调整
- [ ] 直方图计算
- [ ] 自动优化算法

### UI-09: 图像调整 UI
- [ ] 参数滑块面板
- [ ] 实时预览（调整即时生效）
- [ ] 直方图显示组件
- [ ] 重置按钮

### UI-10: 缩略图网格
- [ ] `ui/thumb_view.py` — QScrollArea + 网格布局
- [ ] 缩略图缓存（LRU Cache）
- [ ] 大小滑块调节
- [ ] 双击打开到查看器

### UI-11: 幻灯片播放
- [ ] `ui/slideshow.py` — 全屏窗口
- [ ] 间隔时间设置
- [ ] 随机/顺序播放
- [ ] 键盘控制（暂停/退出）

### UI-12: 文件管理
- [ ] 重命名对话框
- [ ] 删除确认对话框（移至回收站）
- [ ] 复制/移动文件对话框
- [ ] "在资源管理器中显示"

### TEST-03: Phase 3 测试
- [ ] 图像调整单元测试
- [ ] 缩略图缓存测试
- [ ] 文件操作测试

---

## Phase 4 — 高级功能

### CORE-06: RAW 支持
- [ ] `core/raw_loader.py` 实现
- [ ] RawPy 封装
- [ ] CR2/NEF/ARW/RAF/DNG 格式测试
- [ ] 嵌入式 JPEG 预览图提取
- [ ] 基本曝光调整（白平衡、亮度）

### CORE-07: 批处理
- [ ] `core/batch.py` 实现
- [ ] 批量格式转换
- [ ] 批量调整大小
- [ ] 批量重命名
- [ ] 进度回调机制

### UI-13: 批处理界面
- [ ] 批处理对话框
- [ ] 源文件选择
- [ ] 参数配置（目标格式/尺寸/命名模板）
- [ ] 进度条 + 取消按钮
- [ ] 处理结果汇总

### CORE-08: 插件接口
- [ ] `core/interfaces.py` — 抽象基类定义
- [ ] `FormatPlugin` — 格式解析器接口
- [ ] `FilterPlugin` — 图像滤镜接口
- [ ] 插件热加载 (`importlib`)
- [ ] 示例插件 (`plugins/example_plugin.py`)

### TEST-04: Phase 4 测试
- [ ] RAW 加载测试（需要实际 RAW 样本）
- [ ] 批处理测试
- [ ] 插件加载测试
- [ ] 插件接口契约测试

---

## 通用检查项

### 安装与构建
- [ ] `requirements.txt` 依赖列表
- [ ] `requirements-raw.txt` 可选依赖
- [ ] `pip install -e .` 可安装
- [ ] PyInstaller 打包脚本

### 代码质量
- [ ] PEP 8 合规（flake8）
- [ ] 类型注解覆盖（mypy）
- [ ] 文档字符串（核心公共 API）
- [ ] 无硬编码路径

### 测试
- [ ] pytest 运行通过
- [ ] core 层覆盖率 > 85%
- [ ] 所有异常路径有测试覆盖

### 文档
- [x] `spec.md` — 需求规约
- [x] `checklist.md` — 检查清单
- [x] `tasks.md` — 任务分解
- [ ] README.md（如有需要）
