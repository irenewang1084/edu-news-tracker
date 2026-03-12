# 🌐 Global Study Abroad News Tracker

每日自动更新的国际教育新闻追踪器。**完全免费，无需任何 API Key。**

覆盖：中国、东南亚、印度、南亚、西非、拉丁美洲 → 美国、英国、加拿大、澳大利亚、新西兰

---

## ✅ 费用说明

| 服务 | 费用 |
|------|------|
| GitHub | 免费 |
| GitHub Actions（每日自动运行） | 免费（每月 2000 分钟额度，本项目每次约 1 分钟） |
| rss2json.com（RSS 解析） | 免费（每天 1000 次请求，本项目每天用 17 次） |
| Vercel（网页托管） | 免费 |
| **合计** | **¥0 / 月** |

---

## 🚀 部署指南（约 20 分钟）

### 第一步：注册 GitHub（5 分钟）
1. 打开 [github.com](https://github.com) → **Sign up**
2. 填写邮箱、密码、用户名，完成验证，选免费计划

### 第二步：创建仓库并上传文件（5 分钟）
1. 登录后点右上角 **+** → **New repository**
2. Repository name 填：`edu-news-tracker`，选 **Public**，点 **Create repository**
3. 点页面中的 **uploading an existing file**
4. 把本 zip 解压后的**所有文件和文件夹**拖入上传区
5. 点 **Commit changes**

上传后文件结构应为：
```
edu-news-tracker/
├── index.html
├── package.json
├── vite.config.js
├── public/
│   └── news.json          ← 每日自动更新
├── src/
│   ├── main.jsx
│   └── App.jsx
├── scripts/
│   └── fetch_rss.py       ← 免费RSS抓取脚本，无需API Key
└── .github/
    └── workflows/
        └── daily-rss.yml  ← 每日自动运行
```

### 第三步：部署到 Vercel（5 分钟）
1. 打开 [vercel.com](https://vercel.com) → **Sign Up** → **Continue with GitHub**
2. 授权后点 **Add New Project** → 找到 `edu-news-tracker` → **Import**
3. Framework 自动识别为 **Vite**，直接点 **Deploy**
4. 约 1 分钟后获得公开网址，如：`https://edu-news-tracker-xxx.vercel.app`

### 第四步：触发第一次新闻更新（1 分钟）
部署完成后，需要手动触发一次让网页显示新闻：
1. 进入 GitHub 仓库 → 点顶部 **Actions** 标签
2. 左侧点 **Daily RSS Fetch**
3. 右侧点 **Run workflow** → **Run workflow**（绿色按钮）
4. 等待约 1 分钟，完成后 Vercel 自动重新部署

**之后每天北京时间下午 2:00 全自动运行，无需任何操作。**

---

## 🔄 自动更新原理

```
每天 14:00 (北京时间)
    ↓
GitHub Actions 启动
    ↓
Python 脚本抓取 17 个 RSS 源
（经 rss2json.com 免费转换）
    ↓
筛选教育相关文章，标注来源地/目的地/影响力
    ↓
写入 public/news.json
    ↓
推送到 GitHub
    ↓
Vercel 检测到更新，自动重新部署
    ↓
网页内容更新完毕 ✓
```

---

## 📡 RSS 源列表（共 17 个）

| 地区 | 媒体 |
|------|------|
| 🌐 国际专业 | ICEF Monitor · The PIE News · Inside Higher Ed · HEPI · Times Higher Ed · Higher Ed Dive |
| 🇨🇳 中国 | Caixin Global · Sixth Tone · China Daily Education |
| 🇮🇳 印度 | Times of India · The Hindu |
| 🌏 东南亚 | Straits Times · Bangkok Post |
| 🌍 西非 | Guardian Nigeria · Punch Nigeria |
| 🌎 拉丁美洲 | El País · Folha de S.Paulo |

---

## 💬 遇到问题？

截图发给 Claude，可获得逐步帮助。
