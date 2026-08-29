# AGENTS.md — KandelLab 项目指南

## 项目概览
KandelLab 是神经科学原理仿真系统，将 Kandel 教材核心模型逐个用代码实现。
纯前端计算，所有仿真在浏览器内实时运行。

## 技术栈
- Next.js 16 (App Router) + React 19 + TypeScript 5
- Tailwind CSS 4 + shadcn/ui
- 纯 CSS 可视化（无 SVG/Canvas）
- 羊皮纸/中世纪手稿学术风格

## 目录结构
```
src/
├── app/
│   ├── layout.tsx              # 根布局（羊皮纸主题）
│   ├── page.tsx                # 首页
│   ├── cells/                  # 细胞层页面
│   │   ├── nernst/             # Nernst 方程
│   │   ├── goldman/            # GHK 方程
│   │   ├── hodgkin-huxley/     # HH 模型
│   │   ├── lif/                # LIF 模型
│   │   └── synapse/            # 突触模型
│   ├── circuits/               # 回路层页面
│   │   ├── hebbian/            # Hebbian 学习
│   │   ├── lateral-inhibition/ # 侧抑制
│   │   ├── wilson-cowan/       # Wilson-Cowan
│   │   └── kuramoto/           # Kuramoto 同步
│   ├── systems/                # 系统层页面
│   │   ├── vision/             # 视觉系统
│   │   ├── audition/           # 听觉系统
│   │   ├── motor/              # 运动系统
│   │   ├── memory/             # Hopfield 记忆
│   │   └── reward/             # 奖赏学习
│   ├── cognitive/              # 认知层页面
│   │   ├── ddm/                # 漂移扩散模型
│   │   ├── sdt/                # 信号检测论
│   │   └── encoding/           # 群体编码
│   └── experiments/            # 实验总览
├── lib/
│   ├── constants.ts            # 物理/生物常量
│   ├── math-utils.ts           # 数值方法（RK4, 统计函数等）
│   ├── cells/                  # 细胞层仿真模块
│   ├── circuits/               # 回路层仿真模块
│   ├── systems/                # 系统层仿真模块
│   └── cognitive/              # 认知层仿真模块
├── components/
│   ├── simulation-ui.tsx       # 仿真 UI 组件（纯 CSS 图表/热图等）
│   └── ui/                     # shadcn/ui 组件
└── app/globals.css             # 全局样式（羊皮纸主题）
```

## 开发规范
- 所有仿真计算在客户端完成（'use client' 页面直接 import lib 模块）
- 无 API 路由，无后端服务
- 禁止使用 SVG 或 JS 绘图库
- 可视化通过 CSS Grid/Flexbox + div 实现
- 字体：Crimson Pro/Text（衬线）+ JetBrains Mono（等宽）+ Noto Serif SC（中文）

## 构建与检查
- `pnpm ts-check` — TypeScript 类型检查
- `pnpm lint --quiet` — ESLint 检查
- `pnpm build` — 生产构建
