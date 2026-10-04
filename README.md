# MarkdownReader

**[English](README.en.md)** | **[中文](README.md)**

一款现代 Markdown 阅读器：实时预览、暗色/亮色主题、PDF 导出——轻量，零框架依赖。

![MarkdownReader 暗色主题](docs/screenshot-dark.png)

*暗色主题 + 标题大纲面板；下方为亮色主题。*

![MarkdownReader 亮色主题](docs/screenshot-light.png)

## 功能

- **实时预览** — 基于轻量 `QTextBrowser` 的实时渲染（不内置浏览器引擎，启动快）
- **标题大纲** — 侧栏列出全文标题，点击跳转任意章节
- **文件浏览** — 侧栏树形视图，方便在项目目录间切换
- **代码高亮** — 基于 Pygments 的语法高亮，随主题配色（暗色用 `github-dark` 调色板，亮色用 `default`），`Ctrl+Shift+H` 可开关
- **任务列表** — `- [ ]` / `- [x]` 渲染为勾选框
- **本地图片** — 相对路径图片（`![](img.png)`）按文档所在目录解析；网络图片不加载（预览引擎刻意保持离线）
- **GitHub 风格段落** — 默认单个换行不折行（与 GitHub 一致）；偏好硬换行可在视图菜单开启
- **暗色/亮色主题** — `Ctrl+Shift+T` 一键切换，编辑器、预览、界面全部跟随
- **PDF 导出** — `Ctrl+E` 导出当前文档
- **HTML 导出** — 把渲染结果（带主题样式）存为独立 HTML 文件
- **字数统计** — 状态栏实时显示字符/词数（中英文混排分别计数）
- **AI 助手（需自备 API Key）** — 可选功能；右键纠错润色、翻译、总结、解释、续写。任何 OpenAI 兼容服务商均可
- **搜索** — `Ctrl+F` 呼出支持正则的查找栏
- **最近打开** — 文件菜单快速访问最近 10 个文件
- **拖拽打开** — 把 Markdown 文件拖进窗口即可打开
- **编码自动识别** — 自动打开 UTF-8、UTF-8 BOM、GB18030/GBK/GB2312 文件（状态栏显示检测到的编码）；文件永不打不开

## 环境要求

- Python 3.10+
- PyQt5
- Pygments ≥ 2.17
- Markdown

### 支持的文件类型

`.md` `.markdown` `.mdown` `.mkd` `.mkdn` `.mdwn` `.livemd` `.qmd` `.rmd` `.txt` `.text` `.rst` — 均按 Markdown 渲染。

## AI 助手

可选功能——不配置时应用完全离线，功能不受影响。在 **设置 → AI 助手** 中配置：选择服务商预设、粘贴自己的 API Key、填写模型。任何 OpenAI 兼容接口均可：

| 服务商 | 接口地址 |
|--------|----------|
| OpenAI | `https://api.openai.com/v1` |
| DeepSeek | `https://api.deepseek.com/v1` |
| Kimi | `https://api.moonshot.cn/v1` |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| OpenRouter | `https://openrouter.ai/api/v1` |
| Ollama（本地） | `http://localhost:11434/v1` |

在编辑器中选中文字后右键，可用 **纠错润色**、**翻译**（自动判断中英方向）、**总结所选**、**解释这段**（弹窗显示，原文不动）、**续写**、**自定义指令**。

隐私说明：API Key 只保存在本机；请求内容仅发送给你自己配置的服务商——本应用不经手任何数据。

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
# 从项目根目录运行
python -m markdownreader

# 传入文件参数
python -m markdownreader README.md

# 或通过入口脚本（pip install -e . 之后）
markdownreader
```

## 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+O` | 打开文件 |
| `Ctrl+S` | 保存 |
| `Ctrl+Shift+S` | 另存为 |
| `Ctrl+N` | 新建 |
| `Ctrl+W` | 关闭文件 |
| `Ctrl+B` | 切换侧栏 |
| `Ctrl+Shift+T` | 切换主题 |
| `Ctrl+Shift+H` | 切换代码高亮 |
| `Ctrl+F` | 查找 |
| `F3` / `Shift+F3` | 下一个 / 上一个 |
| `Ctrl++` / `Ctrl+-` | 放大 / 缩小 |
| `Ctrl+0` | 重置缩放 |
| `Ctrl+E` | 导出 PDF |
| `F5` | 重新加载 |
| `Ctrl+1` | 聚焦编辑器 |
| `Ctrl+2` | 聚焦预览 |
| `Escape` | 关闭查找栏 |

## 打包

### 便携版 EXE（推荐）

```bash
# Windows —— 双击 build.bat，或执行：
build.bat
```

产物：`dist\MarkdownReader\MarkdownReader.exe`

### 手动 PyInstaller

```bash
pip install pyinstaller
pyinstaller MarkdownReader.spec
```

### 自动发版

推送 `v*` 标签（如 `v1.3.0`）会触发 GitHub Actions 在 Windows 上构建便携版 EXE 并自动附加到 GitHub Release。

### 构建 wheel

```bash
pip install build
python -m build
pip install dist/markdownreader-1.3.0-py3-none-any.whl
```

## 项目结构

```
MarkdownReader/
├── .github/workflows/ci.yml        # push/PR 自动测试
├── .github/workflows/release.yml   # 标签触发自动发版
├── LICENSE
├── MarkdownReader.spec             # PyInstaller 配置（onedir、无窗口）
├── build.bat
├── docs/                           # 截图
├── pyproject.toml
├── requirements.txt
├── tests/                          # pytest 测试
└── markdownreader/
    ├── ai/                         # 可选 AI 助手（需自备 Key）
    │   ├── client.py               #   OpenAI 兼容异步客户端
    │   ├── presets.py              #   服务商预设 + 提示词
    │   ├── assistant.py            #   右键菜单动作控制器
    │   └── settings_dialog.py
    ├── __init__.py                 # 版本号
    ├── __main__.py
    ├── main.py                     # 入口，含崩溃处理
    ├── app.py                      # QApplication 启动
    ├── main_window.py              # 主窗口装配、菜单、状态
    ├── editor.py                   # 编辑器：行号 + Markdown 高亮
    ├── preview.py                  # QTextBrowser 预览面板
    ├── sidebar.py                  # 文件树 + 标题大纲
    ├── search_bar.py
    ├── renderer.py                 # Markdown → 主题化 HTML
    ├── pdf_export.py
    ├── settings.py                 # QSettings 封装
    └── utils.py
```

## 许可证

[MIT](LICENSE)
