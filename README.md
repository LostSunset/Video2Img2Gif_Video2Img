# Video2Img

[![CI](https://github.com/LostSunset/Video2Img2Gif_Video2Img/actions/workflows/ci.yml/badge.svg)](https://github.com/LostSunset/Video2Img2Gif_Video2Img/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/LostSunset/Video2Img2Gif_Video2Img)](https://github.com/LostSunset/Video2Img2Gif_Video2Img/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/LostSunset/Video2Img2Gif_Video2Img)](https://github.com/LostSunset/Video2Img2Gif_Video2Img/network)
[![GitHub issues](https://img.shields.io/github/issues/LostSunset/Video2Img2Gif_Video2Img)](https://github.com/LostSunset/Video2Img2Gif_Video2Img/issues)

影片與圖片轉換工具 - 使用 PySide6 建立的桌面應用程式

## 功能

- **影片 → 圖片**：將任何格式的影片轉換為圖片序列
  - 支援自訂幀間隔（每幾幀輸出一張）
  - 支援多種輸出格式：PNG、JPG、BMP、WebP

- **圖片 → GIF/影片**：將圖片序列轉換為 GIF 動畫或影片
  - 支援批次新增圖片或整個資料夾
  - 可調整 FPS
  - 支援輸出格式：GIF、MP4、AVI、MOV、WEBM

- **影片 → GIF**：將影片直接轉換為 GIF 動畫
  - 支援自訂幀間隔
  - 可調整 GIF FPS
  - 可設定最大寬度以縮小檔案大小

## 安裝

### 使用 uv（推薦）

```bash
# 克隆專案
git clone https://github.com/LostSunset/Video2Img2Gif_Video2Img.git
cd Video2Img2Gif_Video2Img

# 安裝依賴
uv sync

# 執行
uv run video2img
```

### 使用 pip

```bash
pip install -e .
video2img
```

## 開發

```bash
# 安裝開發依賴
uv sync --dev

# 執行 lint 檢查
uv run ruff check .

# 格式化程式碼
uv run ruff format .
```

## 截圖

![Video2Img UI](ui_preview.png)

## 支援的格式

### 輸入影片格式
MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V, MPEG, MPG, 3GP

### 輸入圖片格式
PNG, JPG, JPEG, BMP, WebP, GIF, TIFF, TIF

### 輸出格式
- 圖片：PNG, JPG, BMP, WebP
- 影片：MP4, AVI, MOV, WebM
- 動畫：GIF

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=LostSunset/Video2Img2Gif_Video2Img&type=Date)](https://star-history.com/#LostSunset/Video2Img2Gif_Video2Img&Date)

## 授權

MIT License
