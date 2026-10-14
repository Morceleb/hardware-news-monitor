# hardware-news-monitor

一个用于学习 **CI/CD（GitHub Actions）** 的最小项目：每周自动抓取 DIY 硬件新闻，生成静态网页并发布到 GitHub Pages。

## 项目结构

```
hardware-news-monitor/
├── .github/workflows/weekly-scrape.yml   # GitHub Actions 工作流（核心）
├── scripts/
│   ├── collect.py                        # 抓取 RSS 新闻，写 data/news.json
│   └── build_site.py                     # 读取数据，生成 site/index.html
├── requirements.txt
└── .gitignore
```

## 本地运行

```bash
pip install -r requirements.txt
python scripts/collect.py
python scripts/build_site.py
```

## CI/CD 流程

1. `weekly-scrape.yml` 每周一 09:00（北京时间）自动触发，也可在 Actions 页手动 `Run workflow`。
2. 在 GitHub 提供的 Ubuntu 容器里装依赖 → 采集 → 生成站点。
3. 用 `peaceiris/actions-gh-pages` 把 `site/` 推送到 `gh-pages` 分支。
4. 在仓库 Settings → Pages 里把 Source 设为 `gh-pages` 分支，即可访问 `https://<用户名>.github.io/hardware-news-monitor/`。
