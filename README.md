# CTTAI Skills Collection

一个模块化的 AI 辅助开发与内容创作技能集合，包含 17 个专业技能，覆盖移动开发、前端工程、全栈架构、多媒体生成、文档处理、PPT 制作、Shader 图形编程、微信内容创作、头条号发布以及 AI 自我改进等场景。

---

## 技能总览

| 技能名称 | 路径 | 用途 |
|---|---|---|
| [android-native-dev](#android-native-dev) | `android-native-dev/` | Android 原生应用开发与 UI 设计指南 |
| [frontend-dev](#frontend-dev) | `frontend-dev/` | 全栈前端开发：UI 设计、动画、AI 素材生成、文案 |
| [fullstack-dev](#fullstack-dev) | `fullstack-dev/` | 全栈后端架构与前后端集成方案 |
| [gif-sticker-maker](#gif-sticker-maker) | `gif-sticker-maker/` | 将照片转换为 Funko Pop 盲盒风格的 4 张动态 GIF 贴纸 |
| [ios-application-dev](#ios-application-dev) | `ios-application-dev/` | iOS 应用开发指南（UIKit、SnapKit、SwiftUI） |
| [minimax-docx](#minimax-docx) | `minimax-docx/` | 使用 OpenXML SDK 创建和编辑专业 DOCX 文档 |
| [minimax-multimodal-toolkit](#minimax-multimodal-toolkit) | `minimax-multimodal-toolkit/` | MiniMax 多模态模型：语音、音乐、视频、图片生成 |
| [minimax-pdf](#minimax-pdf) | `minimax-pdf/` | PDF 创建、表单填充与文档样式重塑 |
| [minimax-xlsx](#minimax-xlsx) | `minimax-xlsx/` | Excel 文件的创建、读取、编辑与验证 |
| [pptx-generator](#pptx-generator) | `pptx-generator/` | PowerPoint 演示文稿生成与编辑 |
| [shader-dev](#shader-dev) | `shader-dev/` | GLSL Shader 图形编程：36 种 Shader 技巧 |
| [wechat-article-formatter](#wechat-article-formatter) | `wechat-article-formatter/` | 将 Markdown 文章转换为适合微信公众平台的美化 HTML |
| [wechat-draft-publisher](#wechat-draft-publisher) | `wechat-draft-publisher/` | 自动将 HTML 文章发布到微信公众平台草稿箱 |
| [wechat-product-manager-writer](#wechat-product-manager-writer) | `wechat-product-manager-writer/` | 从 AI 产品经理视角撰写微信文章 |
| [wechat-tech-writer](#wechat-tech-writer) | `wechat-tech-writer/` | 自动搜索、抓取并改写技术内容为微信文章 |
| [self-improving-agent](#self-improving-agent) | `self-improving-agent/` | 持续改进：记录学习、错误与纠正，实现 AI 自我优化 |
| [toutiao-publisher](#toutiao-publisher) | `toutiao-publisher/` | 基于 Playwright 的头条号自动化发布工具 |

---

## 技能详情

### android-native-dev

Android 原生应用开发与 UI 设计指南。

**核心能力**
- Material Design 3 设计规范
- Kotlin/Compose 开发标准
- Gradle 与 AndroidX 项目配置
- 构建变体与产品风味（Build Variants & Product Flavors）
- 无障碍、性能与隐私合规指南

---

### frontend-dev

全栈前端开发技能，整合了高级 UI 设计、电影级动画、AI 素材生成与说服力文案。

**核心能力**
- 设计工程：Tailwind CSS
- 动效系统：Framer Motion、GSAP、Three.js
- AI 素材生成：图片、视频、音频、音乐
- 文案框架：AIDA、PAS、FAB
- 生成式艺术：p5.js
- 多框架模板：React/Next.js、Vue/Nuxt、Astro、纯 HTML

---

### fullstack-dev

全栈后端架构与前后端集成方案。

**核心能力**
- Feature-First 项目结构
- 三层架构：Controller → Service → Repository
- 认证模式：JWT、Session、OAuth
- 错误处理与弹性模式
- 数据库访问与迁移
- API 客户端模式：Typed Fetch、React Query、tRPC、OpenAPI
- 实时通信：SSE、WebSocket、轮询
- 生产环境加固清单

---

### gif-sticker-maker

将照片转换为 4 张 Funko Pop / Pop Mart 盲盒风格的动态 GIF 贴纸。

**工作流**
1. 静态贴纸图生成（MiniMax API）
2. 图生视频动画
3. 视频转 GIF（FFmpeg）
4. 多语言 caption 支持
5. 并发生成

---

### ios-application-dev

iOS 应用开发指南，覆盖 UIKit、SnapKit 和 SwiftUI。

**核心能力**
- Apple Human Interface Guidelines 合规
- 触控目标、安全区域、导航模式
- Dynamic Type 与无障碍支持
- 深色模式适配
- Collection Views 与通用 UI 组件
- SwiftUI 设计规范

---

### minimax-docx

使用 OpenXML SDK（.NET）创建、编辑与格式化专业 DOCX 文档。

**三条管线**
- **CREATE**：从零生成新文档
- **FILL-EDIT**：填充与编辑现有文档
- **FORMAT-APPLY**：应用格式化样式

**核心能力**
- C# 脚本 + OpenXML SDK
- XSD 验证门控
- 基于模板的文档生成
- 多章节页眉/页脚支持
- 学术、商业、政府文档样式

---

### minimax-multimodal-toolkit

MiniMax 多模态模型，支持语音、音乐、视频、图片生成。

**核心能力**
- **TTS**：文本转语音，支持语音克隆与声音设计
- **音乐生成**：歌曲与器乐曲
- **图片生成**：文生图、图生图
- **视频生成**：文生视频、图生视频、多场景视频
- **媒体处理工具**：转换、拼接、裁剪、提取
- FFmpeg 音视频工作流

---

### minimax-pdf

PDF 创建、表单填充与文档样式重塑。

**三条管线**
- **CREATE**：使用设计令牌从零生成 PDF
- **FILL**：填写现有 PDF 表单字段
- **REFORMAT**：为现有文档应用设计样式

**核心能力**
- 15 种文档类型模板（报告、提案、简历、学术论文等）
- 基于令牌的设计系统（颜色、排版、间距）

---

### minimax-xlsx

Excel/电子表格文件的创建、读取、编辑与验证。

**四条管线**
- **READ**：用 xlsx_reader.py + pandas 分析现有数据
- **CREATE**：从 XML 模板创建新 xlsx
- **EDIT**：XML 解包/编辑/打包，不丢失格式
- **VALIDATE**：用 formula_check.py 验证公式

**核心能力**
- 修复损坏的公式
- 金融配色标准（蓝色=输入，黑色=公式，绿色=跨表引用）

---

### pptx-generator

PowerPoint 演示文稿生成与编辑。

**核心能力**
- 使用 PptxGenJS 从零创建
- 5 种幻灯片类型：封面、目录、分隔页、内容页、总结页
- 完整设计系统：配色方案、字体、样式配方
- 基于 XML 的模板编辑
- markitdown 文本提取

---

### shader-dev

GLSL Shader 图形编程技能。

**核心能力**
- 36 种 Shader 技巧（兼容 ShaderToy）
- 射线 marching 与 SDF 建模
- 流体模拟与粒子系统
- 程序化生成与噪声函数
- 光照模型：PBR、Phong、卡通
- 后处理效果

---

### wechat-article-formatter

将 Markdown 文章转换为适合微信公众平台发布的美化 HTML。

**核心能力**
- 专业 CSS 样式与代码高亮
- 三种主题：技术风格、简约风格、商务风格
- 预置模板：VSCode 蓝、红蓝对比、极客暗色、现代简约
- 代码块转换以适配微信
- 与 wechat-tech-writer 集成

---

### wechat-draft-publisher

自动将 HTML 文章发布到微信公众平台草稿箱。

**核心能力**
- 封面图片上传与管理
- 标题、作者、摘要元数据
- access_token 自动缓存
- HTML 内容优化以适配微信
- 与 wechat-article-formatter 工作流集成

---

### wechat-product-manager-writer

从 AI 产品经理视角撰写微信文章。

**核心能力**
- 5 种内容类型：AI 产品拆解、场景解决方案、效率技巧、产品方法论、行业观察
- 第一人称叙事风格
- 要求真实使用场景
- 强制封面图 + 内容结构图生成
- 使用 Gemini API 生成图片（含代理处理）

---

### wechat-tech-writer

自动搜索、抓取并改写技术内容为微信中文科普文章。

**核心能力**
- 覆盖主题：AI 模型、GitHub 开源工具、技术专题
- WebSearch + WebFetch 研究工作流
- 强制封面图生成
- 每篇文章 0-2 张内容图（数据对比、架构图）
- 纯文本链接格式（无 Markdown 超链接）

---

### self-improving-agent

持续改进技能，记录学习、错误与纠正，实现 AI 自我优化。

**核心能力**
- **学习日志**：记录纠正、知识差距、最佳实践
- **错误追踪**：命令失败、异常、API 问题
- **功能请求**：用户请求但缺失的能力
- **晋升机制**：将通用学习提升到项目记忆（CLAUDE.md、AGENTS.md）
- **多 Agent 支持**：Claude Code、Codex、Copilot、OpenClaw

**日志格式**
- `LEARNINGS.md` — 纠正与最佳实践
- `ERRORS.md` — 命令失败与异常
- `FEATURE_REQUESTS.md` — 功能请求

---

### toutiao-publisher

基于 Playwright 的头条号自动化发布工具，模拟真实用户行为进行发布。

**核心能力**
- **智能填充**：多级降级策略（execCommand > ClipboardEvent）确保内容注入成功
- **封面自动化**：支持本地图片上传
- **即时登录**：检测未登录状态自动暂停，等待用户扫码
- **状态持久化**：Cookie 和 LocalStorage 复用，免登录
- **反爬虫策略**：配置反检测浏览器上下文

**工作流**
1. 检测登录状态，未登录则等待扫码
2. 填充标题与正文（支持 Markdown）
3. 上传封面图片
4. 点击发布并确认

---

## 技能通用模式

### 目录结构约定

大多数技能遵循一致的目录布局：

```
skill-name/
├── SKILL.md              # 主入口文件，含使用说明
├── scripts/              # 可执行脚本
├── references/           # 详细文档（按需阅读）
├── templates/            # 模板文件（可选）
├── assets/               # 静态资源（可选）
└── examples/             # 示例文件（可选）
```

### API 集成

| API | 使用技能 |
|---|---|
| MiniMax API | `gif-sticker-maker`, `minimax-multimodal-toolkit` |
| Gemini API | `wechat-product-manager-writer`, `wechat-tech-writer` |
| WeChat API | `wechat-draft-publisher` |

常用环境变量：`MINIMAX_API_KEY`、`MINIMAX_API_HOST`、`GEMINI_API_KEY`

### 微信内容管线

三个微信技能形成完整工作流：

```
wechat-tech-writer / wechat-product-manager-writer
        ↓ 生成文章（.md + cover.png）
wechat-article-formatter
        ↓ 转换为美化 HTML
wechat-draft-publisher
        ↓ 发布到微信草稿箱
```

### 文档处理链

`minimax-docx`、`minimax-pdf`、`minimax-xlsx`、`pptx-generator` 均有类似的操作管线：
1. 先读取现有文件
2. 使用特定脚本执行操作
3. 输出为标准格式

### 验证模式

- **minimax-docx**：编辑后 XSD 验证
- **minimax-xlsx**：formula_check.py 公式校验
- **pptx-generator**：QA 流程与避坑清单

---

## 许可证

所有技能均采用 MIT 许可证。
