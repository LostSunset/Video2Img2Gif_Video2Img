# Video2Img 專案開發規範

## 專案資訊

- **倉庫**: https://github.com/LostSunset/Video2Img2Gif_Video2Img.git
- **Python 版本**: 3.14
- **套件管理器**: uv（禁止使用 pip）
- **虛擬環境**: .venv314

---

## 專案環境管理

1. **套件管理器**：一律使用 uv，禁止使用 pip 或其他工具
2. **Python 版本**：3.14
3. **虛擬環境名稱**：.venv314
4. **啟動環境指令**：`source .venv314/bin/activate` 或 `uv run`

---

## 正體中文 / UTF-8 支援（必做）

1. **檔案編碼**：專案所有文字檔（.py/.toml/.ini/.md/.txt）一律以 UTF-8 存檔
2. **讀寫明確指定**：測試資料（fixtures/golden files）含中文時，讀寫一律明確指定 `encoding="utf-8"`
3. **測試輸出**：執行時強制 UTF-8 輸出，設定 `PYTHONIOENCODING=utf-8`
4. **CI 編碼一致**：
   - Linux：設定 `LANG=en_US.UTF-8` 和 `LC_ALL=en_US.UTF-8`
   - Windows：確保終端 codepage/輸出不破字
5. **pytest 輸出**：assertion/差異輸出需可正確顯示中文，log 不可出現亂碼

---

## 必要工具檢查

每次開始工作前，確認以下工具已安裝並設定好環境路徑：
- npx（ralph-loop 需要）
- jq（ralph-loop 需要）

如未安裝，請執行安裝並設定環境路徑。

---

## 工作流程

1. **每次任務執行格式**：
   ```
   /ralph-loop:ralph-loop "<填寫具體任務描述>" --completion-promise "DONE"
   ```

2. **程式碼審查流程**：
   - 永遠先用 Codex 來 review 程式碼
   - 有不清楚、疑問、疑惑之處都問 Codex
   - 使用 Codex 時一律使用最新的思考模型

3. **每完成一個 Session 後**：
   - 執行 lint 檢查與自動修復
   - 提交變更到 GitHub
   - 控制版本，確保程式碼可救回

---

## GitHub 倉庫設定

### Lint 檢查與自動修復（推送前必做）

```bash
# 自動修復格式
ruff format .

# 自動修復 import 等
ruff check --fix .

# 最終檢查
ruff check .
```

### 常見 Lint 問題修復方式

| 錯誤碼 | 問題描述 | 修復方式 |
|--------|----------|----------|
| W293 | 空白行包含多餘空格 | `ruff format` 自動修復 |
| E722 | 使用 bare `except:` | 改為 `except Exception:` |
| I001 | import 未排序 | `ruff check --fix` 自動修復 |
| F401 | 未使用的 import | 刪除或加 `# noqa: F401` |
| NameError | forward reference | 檔案開頭加 `from __future__ import annotations` |

### README 徽章（必須加入）

- CI 狀態徽章
- License: MIT 徽章
- Python 3.10+ 徽章
- GitHub stars 徽章
- GitHub forks 徽章
- GitHub issues 徽章
- Star History 圖表

---

## Release Agent 自動發布流程

建立一個名為 `release` 的 user-level agent，負責：

1. 自動執行測試（`uv run pytest`）
2. 執行 lint 檢查與修復
3. 更新 README（如有需要）
4. 根據變更類型更新版本號
5. 提交變更並標記版本
6. 推送到 GitHub

---

## 版本規則（Semantic Versioning）

每一次推送更新都要往上增加一個版本：

| 變更類型 | 版本變更 | 範例 |
|----------|----------|------|
| Bug 修復或效能提升 | PATCH | v0.0.1 → v0.0.2 |
| 新功能 | MINOR | v0.0.1 → v0.1.0 |
| 重大變更（Breaking Changes） | MAJOR | v0.0.1 → v1.0.0 |

### Commit 類型對應

- `fix:` → Bug 修復（PATCH）
- `feat:` → 新功能（MINOR）
- `breaking:` → 重大變更（MAJOR）

---

## Claude Code 最佳實踐

### 多工並行處理

- 同時開啟 3-5 個 git worktree，每個執行獨立的 Claude 工作階段並行運作
- 設定 shell 別名（za、zb、zc）只需一鍵就能快速切換
- 建立專用「分析」worktree，專門用來查看日誌和執行 BigQuery

### 計畫模式優先

- 複雜任務一律從計畫模式開始
- 把心力投入計畫，讓 Claude 能一次到位完成實作
- 一旦事情偏離軌道，立刻切回計畫模式重新規劃，不要硬著頭皮繼續
- 在驗證步驟時也要進入計畫模式，不只是在建構階段

### CLAUDE.md 維護

- 每次糾正 Claude 後，都加上：「更新你的 CLAUDE.md，這樣以後就不會再犯同樣的錯」
- 持續精煉 CLAUDE.md，不斷迭代，直到錯誤率明顯下降
- 為每個任務/專案維護一個筆記目錄，每次 PR 後更新，並在 CLAUDE.md 中指向這個目錄

### 技能與指令

- 如果某件事一天做超過一次，就把它變成技能或指令
- 建立 /techdebt 斜線指令，每次工作結束時執行，找出並消除重複的程式碼
- 設定一個斜線指令，將過去 7 天的 Slack、GDrive、Asana 和 GitHub 同步整合成一份完整的上下文摘要
- 打造分析工程師風格的代理程式，用來撰寫 dbt 模型、審查程式碼，並在開發環境中測試變更

### Bug 修復

- 啟用 Slack MCP，把 Slack 上的 bug 討論串貼給 Claude，只說「fix」，完全不需要切換情境
- 直接說「去修好失敗的 CI 測試」，不用事必躬親地指導怎麼做
- 讓 Claude 查看 docker logs 來排查分散式系統問題，它在這方面的能力出奇地強

### 提示技巧

- 挑戰 Claude：說「針對這些變更嚴格考問我，在我通過測試之前不要建立 PR」，讓 Claude 當你的審查者
- 說「向我證明這行得通」，讓 Claude 比較 main 分支和功能分支之間的行為差異
- 在得到一個普通的修復後，說：「根據你現在所知的一切，砍掉重練，實作出優雅的解決方案」
- 交付工作前先撰寫詳細的規格說明，減少模糊地帶，你越具體，產出就越好

### 終端機與環境設定

- 使用 /statusline 自訂狀態列，讓它隨時顯示上下文使用量和目前的 git 分支
- 善用語音輸入，說話的速度是打字的 3 倍，而且提示會變得更加詳盡（macOS 按兩下 fn 鍵）

### 子代理使用

- 在任何需要 Claude 投入更多運算資源的請求後面加上「use subagents」
- 將個別任務分派給子代理，保持主代理的上下文視窗乾淨且專注
- 透過 hook 將權限請求路由到 Opus 4.5，讓它掃描攻擊並自動批准安全的請求

### 數據分析

- 讓 Claude Code 使用 bq CLI 即時拉取和分析指標
- 這適用於任何有 CLI、MCP 或 API 的資料庫

### 學習模式

- 在 /config 中啟用「Explanatory」或「Learning」輸出風格，讓 Claude 解釋變更背後的「為什麼」
- 讓 Claude 產生視覺化的 HTML 簡報來解釋不熟悉的程式碼
- 請 Claude 繪製 ASCII 圖表來呈現新的協定和程式庫架構，幫助理解

---

## PySide6 UI 視覺回饋開發流程

### 核心概念

在開發 PySide6 UI 時，你必須能夠「看到」實際渲染結果來理解排版問題。使用離屏渲染（offscreen rendering）將 UI 截圖輸出為圖片，然後查看該圖片來分析佈局。

### 強制工作流程（RALPH Loop 擴展）

每次修改 UI 代碼後，必須執行以下步驟：

1. 保存 UI 代碼
2. 執行離屏截圖腳本，生成 ui_preview.png
3. 使用 view 工具查看截圖
4. 分析排版問題，基於視覺結果判斷：
   - 元件對齊是否正確
   - 間距是否合理
   - 字體大小是否適當
   - 整體佈局是否平衡
5. 根據觀察修改代碼，回到步驟 1

### 離屏截圖腳本

在專案根目錄創建 `_ui_preview.py`：

```python
#!/usr/bin/env python3
"""
PySide6 UI 離屏渲染截圖工具
用法: python _ui_preview.py [模組路徑] [類別名稱] [寬度] [高度]
範例: python _ui_preview.py src.main_window MainWindow 1280 720
"""
import sys
import os
import importlib

# 設置 offscreen 平台（必須在 QApplication 之前）
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

def capture_ui(module_path: str, class_name: str, width: int = 1280, height: int = 720):
    app = QApplication(sys.argv)

    # 動態導入模組和類別
    module = importlib.import_module(module_path)
    WindowClass = getattr(module, class_name)

    # 創建並顯示視窗
    window = WindowClass()
    window.resize(width, height)
    window.show()

    # 確保完全渲染後截圖
    def do_capture():
        app.processEvents()
        pixmap = window.grab()
        output_path = "ui_preview.png"
        pixmap.save(output_path)
        print(f"UI 截圖已保存至: {output_path}")
        app.quit()

    # 延遲執行確保渲染完成
    QTimer.singleShot(200, do_capture)
    app.exec()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python _ui_preview.py <模組路徑> <類別名稱> [寬度] [高度]")
        print("範例: python _ui_preview.py src.main_window MainWindow 1280 720")
        sys.exit(1)

    module_path = sys.argv[1]
    class_name = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 720

    capture_ui(module_path, class_name, width, height)
```

### 快速截圖命令

```bash
# 基本用法
python _ui_preview.py <模組路徑> <類別名稱>

# 指定尺寸
python _ui_preview.py src.main_window MainWindow 1920 1080

# 截圖後確認
python _ui_preview.py src.main_window MainWindow && echo "截圖完成"
```

### 行為準則

1. **永遠不要盲目修改 UI** — 每次修改後必須截圖查看結果
2. **主動截圖** — 不要等用戶要求，修改 UI 後自動執行截圖流程
3. **描述你看到的** — 查看截圖後，向用戶描述你觀察到的排版狀況
4. **迭代優化** — 如果排版有問題，說明問題並提出修改建議，修改後再次截圖驗證

### 常見排版檢查點

查看截圖時注意：
- 元件是否被裁切或溢出
- 文字是否可讀（大小、對比度）
- 按鈕/輸入框大小是否合適
- 邊距和間距是否一致
- 視覺層級是否清晰
- 響應式佈局在指定尺寸下是否正常

### 多狀態截圖（進階）

如需測試不同 UI 狀態，可擴展腳本：

```python
def capture_with_state(window, state_name: str, setup_func):
    """截圖特定 UI 狀態"""
    setup_func(window)  # 設置狀態（如填入數據、切換頁面）
    app.processEvents()
    pixmap = window.grab()
    pixmap.save(f"ui_preview_{state_name}.png")
```

---

## 開發進度

（待記錄當前開發進度）

---

## 錯誤紀錄

每次 Claude 犯錯後，在此區塊新增紀錄，避免再犯：

1. （待記錄）
2. （待記錄）
3. （待記錄）
