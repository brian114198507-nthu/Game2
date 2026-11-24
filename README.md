# 夢境存錢旅：月光鑰匙

一款繁體中文、瀏覽器可玩的 Godot 4 教育小遊戲。玩家陪飛蛾旅人阿露穿越月光鐘樓，完成兩道理財挑戰、取得鑰匙並回顧本次遊戲分數。

## 本機執行

1. 使用 Godot 4.7.2 開啟這個資料夾（選取 `project.godot`）。
2. 匯入資源完成後，按 F6/F5 或從主場景執行。
3. Blender 原始模型在 `assets/models/moon_moth.blend`；`tools/create_blender_assets.py` 可用 Blender 5.3 重建並匯出遊戲使用的 `moon_moth.glb`。Godot 專案直接載入 GLB，避免在匯出時依賴 Blender 匯入器。
4. 繁體中文字型 Noto Sans TC 及 OFL 授權檔位於 `assets/fonts/`。

Noto Sans TC 依 SIL Open Font License 1.1 授權；完整條文見 `assets/fonts/OFL.txt`。

## Web 匯出

此專案使用 Godot GDScript 和 Compatibility renderer，可匯出 Godot Web（WebAssembly/WebGL 2）。這台開發機已安裝 Godot 4.7.2 對應的 Web debug/release 模板；其他環境請安裝相同版本的 Web 模板。

1. 若在其他電腦匯出，請在 Godot 的 **Editor → Manage Export Templates** 安裝 4.7.2 Web 匯出模板。
2. 執行 `powershell.exe -ExecutionPolicy Bypass -File .\build_web.ps1`，匯出至 `docs/index.html`；或在 **Project → Export** 選取 Web 預設並匯出到 `docs/index.html`。
3. 本機檢視請以 HTTP 靜態伺服器提供 `docs/` 目錄（不要直接以 `file://` 開啟）。

## GitHub Pages

把此專案推送到 GitHub，在 **Settings → Pages → Deploy from a branch** 選擇 `main` 分支和 `/docs`。`docs/` 已包含匯出成品與 `.nojekyll`。

## Netlify

可直接把 `docs/` 目錄拖到 Netlify，或連結 GitHub 儲存庫；根目錄 `netlify.toml` 已將 Publish directory 設為 `docs`，並提供 MIME 與快取標頭。

## 遊戲規則與分數

- **關卡 1：雨夜的預算門**：10 枚星幣，先買 4 枚的雨衣並留下 6 枚替 8 枚的暖光燈存錢。答錯可看回饋再試，不會扣掉遊戲中的星幣。
- **關卡 2：夢樹花園**：6 枚星幣中，安全留下至少 2 枚供明天車票使用，其餘投資分散到兩株夢樹。結果展示一株減少、一株增加，說明投資有風險而且不保證回報。
- 每關滿分 100，正確性為主；首次答對且思考時間不超過 25 秒才得到最多 5 分速度加分。提示後仍可完成並取得鑰匙。
- 結尾分數與徽章表示本次遊戲行為，不是正式學習成效測驗。沒有帳號、外部追蹤或真實交易。

設計、證據標籤和評量假設見 [`GAME_DESIGN.md`](GAME_DESIGN.md)。
