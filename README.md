# 🏛️ 六爻象数营造与典籍引证系统 (LiuYao 3D Digital Aesthetic System)

[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](https://opensource.org/licenses/MIT)
[![Docker Support](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Three.js](https://img.shields.io/badge/Frontend-Three.js_r128-black.svg)](https://threejs.org/)
[![Visual Style](https://img.shields.io/badge/Aesthetic-Neo--Chinese_Tekton-red.svg)](#-设计美学与营造法式)

> 融汇宋代《营造法式》大木作精髓与现代 WebGL 物理渲染（PBR）的先锋数字国风六爻排盘、典籍实证与 AI 解卦系统。

---

## ✨ 核心特性

### 1. 🎨 先锋数字国风 · 3D 象数营造
* **大木作金镶玉月梁**：深色黑檀木架构件包边，贯穿羊脂温润白玉透光内芯；动爻呈现深邃朱砂血玉质感与内部微发光脉冲。
* **物理变爻动效**：彻底抛弃突兀的金属贴片与假挂件，老阳（9点）微动渐裂、老阴（6点）合龙聚首，符合易象之演化。
* **下沉式汉白玉须弥金池**：汉白玉叠涩基台搭配内凹金池，上方悬浮多层真 3D 实体金属管状浑天仪环，并带柔和自转与地脉金晕。
* **高精法线阳文乾隆通宝**：三枚铜钱通过梯度高度差生成 Normal Map，正反面真字清晰立体，侧光下浮雕阴影分明。
* **4K 原生矢量 DOM 悬牌**：利用屏幕投影向量（Screen Projection）在三维空间实时同步 HTML5 标签，彻底根除 3D 贴图模糊与边缘走样。
* **零延迟轻量级碰撞（BVH/HitBox Proxy）**：以极低算力实现精准拾取，保持原生 60FPS 流畅度，点击任意构件即刻滑出【爻象玄机 · 二级研读抽屉】。

### 2. 📜 严谨学理 · 十大典籍引证引擎
* **全卦象自动考据**：内置《增删卜易》、《卜筮正宗》、《黄金策》、《火珠林》实占规则链。
* **动静皆备**：无论动爻变克（回头生、回头克），还是静卦旺衰、逢空（旬空出空）、逢破（日破月破）、伏神隐现，系统皆可自动提取古典原典章节与大白话断语。

### 3. 🤖 深度大模型全盘推演
* **双模易学 Prompt 引擎**：自动编排结构化象数考据 Prompt，支持复制。
* **支持自定义大模型接入**：支持在前端通过对话框直接填入兼容 OpenAI / DeepSeek / 通义千问等接口的 API Key 与 Base URL，即时生成通俗易懂的长文决策研读。

---

## 🛠️ 技术栈架构

```text
liuyao_system/
├── backend/
│   └── app/
│       ├── core/          # 六爻象数核心算法、排盘、时空纳甲与典籍考据知识库
│       └── main.py        # FastAPI 高性能异步服务与接口路由
├── frontend/
│   ├── css/style.css      # 新中式数字展陈样式、磨砂玻璃 HUD 与二级抽屉动效
│   ├── js/scene3d.js      # Three.js 3D 金镶玉月梁、管状浑天仪与碰撞拾取引擎
│   ├── js/app.js          # 交互编排、排盘状态机与大模型流式调用
│   └── index.html         # 响应式主视图与矢量投影字牌容器
├── docker-compose.yml     # 标准化单机编排配置（含健康检查与持久挂载）
└── Dockerfile             # 极简轻量级 Python 运行时容器

---

## 🛠️ 技术栈架构

```text
liuyao_system/
├── backend/
│   └── app/
│       ├── core/          # 六爻象数核心算法、排盘、时空纳甲与典籍考据知识库
│       └── main.py        # FastAPI 高性能异步服务与接口路由
├── frontend/
│   ├── css/style.css      # 新中式数字展陈样式、磨砂玻璃 HUD 与二级抽屉动效
│   ├── js/scene3d.js      # Three.js 3D 金镶玉月梁、管状浑天仪与碰撞拾取引擎
│   ├── js/app.js          # 交互编排、排盘状态机与大模型流式调用
│   └── index.html         # 响应式主视图与矢量投影字牌容器
├── docker-compose.yml     # 标准化单机编排配置（含健康检查与持久挂载）
└── Dockerfile             # 极简轻量级 Python 运行时容器

```

---

## 🚀 极速部署指引（适用于任何新机器）

### 前置要求

* 目标服务器已安装 **Git** 与 **Docker / Docker Compose**。

### 1. 克隆项目仓库

```bash
git clone [https://github.com/xumingzhao0401-blip/liuyao.git](https://github.com/xumingzhao0401-blip/liuyao.git)
cd liuyao

```

### 2. 一键构建并启动

```bash
docker compose up -d --build

```

### 3. 访问与使用

启动完成后，在浏览器访问：

```text
http://<你的服务器IP>:8000

```

* 点击顶部 **`🏛️ 切换 3D 营造视界`** 体验沉浸式三维象数营造。
* 点击任意木梁或悬牌，右侧自动展开二级大白话详解抽屉。
* 点击右上角 **`⚙️ 模型与API`** 可以直接输入你的大模型 API Key 启用全自动智能断卦。

---

## ⚙️ 环境变量与配置说明

系统已内置 `.env.example`，敏感 Token 绝不上库。如果需要在服务端注入默认大模型配置，可在根目录新建 `.env`：

```bash
cp .env.example .env

```

`.env` 常用字段：

```ini
# 大模型配置（可选；若留空，用户依然可在前端界面临时输入）
AI_API_KEY=
AI_API_BASE=[https://api.deepseek.com/v1](https://api.deepseek.com/v1)
AI_MODEL_NAME=deepseek-chat

```

---

## 🔍 服务自检与冒烟测试

在服务器终端执行以下命令，快速验证算法排盘与引证引擎是否正常运行：

```bash
curl -s -X POST [http://127.0.0.1:8000/api/divine](http://127.0.0.1:8000/api/divine) \
  -H "Content-Type: application/json" \
  -d '{"manual_sums": [7, 8, 7, 8, 9, 8], "question": "项目推进与发展吉凶"}' | jq '{status: .status, hex_name: .hexagram.original_name, line_count: (.lines | length), evidence_count: (.evidences | length)}'

```

---

## 📄 开源许可证

本项目基于 [MIT License](https://www.google.com/search?q=LICENSE&utm_source=gemini) 开源。

```

```
