# TimeTree Exporter

[English](README.md) | [繁體中文](README.zh-tw.md)

[![PyPI](https://img.shields.io/pypi/v/timetree-exporter.svg)](https://pypi.org/project/timetree-exporter/)
[![Python 3.x](https://img.shields.io/pypi/pyversions/timetree-exporter.svg?logo=python&logoColor=white)](https://pypi.org/project/timetree-exporter/)
[![License](https://img.shields.io/github/license/eoleedi/TimeTree-Exporter)](https://github.com/eoleedi/TimeTree-Exporter/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/timetree-exporter)](https://pypistats.org/packages/timetree-exporter)
[![Buy Me A Coffee](<https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg?logo=buymeacoffee&logoColor=white>)](https://www.buymeacoffee.com/eoleedi)

將 TimeTree 行事曆匯出並轉換為 iCalendar 格式（.ics）的工具（相容於 [RFC 5545](https://datatracker.ietf.org/doc/html/rfc5545)，並支援部分 [RFC 7986](https://datatracker.ietf.org/doc/html/rfc7986) 屬性）。
這個程式透過擷取 TimeTree 網頁版的資料，將其轉換為 iCal 格式。
（產生的 .ics 檔案可匯入 Google 日曆、Apple 行事曆、Outlook 行事曆等其他行事曆！）

> [!Warning]
> 本專案由開源社群獨立開發，與 TimeTree, Inc. 並無關聯。
> 本工具使用非官方、透過逆向工程取得的 TimeTree 網頁 API，這些 API 可能隨時變更或停止運作，且不會另行通知，所以要注意工具可能會突然失效歐！
> 請合理使用：短時間內傳送過多請求，可能導致 TimeTree 限制請求頻率、暫時封鎖或採取其他限制措施。

## 安裝

> [!Note]
> TimeTree Exporter 需要 Python 3.10 或更新版本。

如果你使用 macOS，可以透過 Homebrew 安裝：

```bash
brew install eoleedi/tap/timetree-exporter
```

也可以使用 uvx、pip 或 pipx 安裝：

```bash
pip install timetree-exporter
```

## 使用方式

```bash
timetree-exporter -o path/to/output.ics
```

會指示你輸入 TimeTree 的電子郵件地址與密碼，並選擇要匯出的行事曆。

接著，即可將 ICS 檔案匯入你的行事曆應用程式。

> [!Note]
> 💡 建議將 ICS 檔案匯入獨立的行事曆（例如在 Google 日曆中新增一個行事曆），若發生問題，只要刪除該行事曆後重新匯入即可。

### 進階使用方式

- 使用 `-e` 選項指定電子郵件地址。

  ```bash
  timetree-exporter -e email@example.com
  ```
- 使用 `-c` 或 `--calendar_code` 選項指定行事曆代碼。

  ```bash
  timetree-exporter -c calendar_code
  ```

  注意：可從行事曆頁面的網址取得行事曆代碼，或在不帶 `-c` 選項的情況下執行程式來查看。
- 透過 ID 匯出公開行事曆，無須登入。

  ```bash
  timetree-exporter --public-calendar -c public_calendar_id
  ```

  注意：公開行事曆活動使用 TimeTree 的公開 API，可能不包含標籤、提醒、重複規則或 UUID。
  若有提供來源連結、圖片與顏色等公開行事曆中繼資料，會以 `SOURCE`、`IMAGE` 和 `COLOR` 等 RFC 7986 屬性匯出。僅實作 RFC 5545 的行事曆應用程式可能會忽略這些選用欄位。
- 可透過環境變數傳入電子郵件地址與密碼（通常用於自動化作業）。

  ```bash
  export TIMETREE_EMAIL=email@example.com
  export TIMETREE_PASSWORD=password
  ```
- 依標籤分別建立 ICS 檔案，並可自訂輸出目錄。

  ```bash
  timetree-exporter --split-by-label
  ```

  這會為每個標籤建立獨立的 ICS 檔案（例如 `timetree_work.ics`、`timetree_personal.ics`）。
- 包含私人行事曆活動的留言。

  ```bash
  timetree-exporter --include-comments
  ```

  留言會從 TimeTree 的活動動態端點擷取，並匯出為 iCalendar 的 `COMMENT` 屬性；若有作者姓名，會加在留言前方。

  若要調整擷取留言時同時的請求量，可以用 `--num-workers`。

  ```bash
  timetree-exporter --include-comments --num-workers 5
  ```

  預設為 `10`。

  > [!Caution]
  > 此選項預設關閉，因為每個活動都需要額外向 TimeTree 發送一個或多個請求。大型行事曆的匯出速度可能較慢，也可能觸發 TimeTree 的請求頻率限制。
  >
- 包含私人行事曆活動的附加圖片。

  ```bash
  timetree-exporter --include-images --num-workers 2
  ```

  圖片會儲存在 ICS 輸出檔案旁的 `timetree_images/` 目錄中，並依活動 UUID 分組。
  `timetree_images.json` 檔案會記錄每張圖片對應的活動 UUID、標題、開始日期、物件索引鍵及相對路徑。
  已存在的圖片檔案會被略過，因此可以安全地再次執行匯出。
  此選項僅適用於私人行事曆，並會額外發送活動動態與圖片請求。

## 限制

- TimeTree 標籤包含分類名稱與顏色。使用 `--split-by-label` 時，每個分類會儲存為獨立的 ICS 檔案。
- 標籤顏色資訊會保留在 ICS 輸出中，但 Google 日曆匯入 ICS 檔案時，不會套用這些活動顏色。如果你依賴顏色來整理活動，可能需要回到 TimeTree 查看過往的顏色資訊。
- TimeTree 活動的備註會匯出為 iCalendar 的 `DESCRIPTION`。私人行事曆活動的留言僅在使用 `--include-comments` 時才會匯出。

## 開發

開發環境設定與貢獻方式，請參閱 [DEVELOPMENT.md](DEVELOPMENT.md)。

## 支持

如果你覺得這個工具有幫助，歡迎支持抖內！

[![請我喝杯咖啡](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/eoleedi)
