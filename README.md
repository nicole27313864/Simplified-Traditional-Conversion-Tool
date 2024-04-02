# 簡繁轉換工具

這是一款基於 PySide6 開發的簡繁轉換工具，可用於將指定資料夾中的檔案或使用者輸入的文本進行簡繁轉換。支援多種簡繁轉換格式，包括台灣化、中國化、繁體化和簡體化。

## 功能特點

- **多種簡繁轉換格式：** 提供多種簡繁轉換格式選擇，讓使用者自由選擇適合的轉換格式。
- **多種格式支援：** 可以指定需要轉換的檔案副檔名，例如 Text、Yaml、HTML、CSS、JavaScript 等，以滿足不同的需求。
- **路徑模式和文本模式：** 支援路徑模式和文本模式，可選擇轉換資料夾中的檔案或直接轉換使用者輸入的文本。
- **UI 介面友好：** 使用 PySide6 庫開發，提供直觀的使用者介面，讓使用者可以輕鬆操作。
- **轉換進度即時顯示：** 轉換進度即時顯示，方便使用者了解轉換過程。
- **一鍵複製結果：** 支援一鍵複製轉換結果到剪貼板，方便使用者快速分享或使用轉換後的內容。

## 使用說明

1. **選擇資料夾模式：**
   - 點擊「請選擇路徑」按鈕選擇待轉換檔案所在的資料夾。
   - 輸入欲轉換的檔案副檔名，可使用空格、換行或逗號區分，如「html, js, css, text, yaml」。
   - 選擇轉換格式。
   - 點擊「開始轉換」按鈕執行轉換操作。

2. **文本模式：**
   - 在文本輸入框中輸入待轉換的文本。
   - 選擇轉換格式。
   - 點擊「開始轉換」按鈕執行轉換操作。

## 技術細節

- 使用 PySide6 構建使用者介面。
- 使用 OpenCC 庫進行繁簡轉換。
- 使用 Qt Material 樣式表進行介面美化。

## 注意事項

- 請注意在使用前安裝必要的依賴庫，包括 PySide6、opencc-python-reimplemented 和 qt_material。
- 使用前請確保已選擇正確的資料夾和檔案副檔名。
- 轉換過程中請勿關閉程式視窗，以免影響轉換操作。

如果有任何問題或建議，歡迎提出 Issue 或者提交 Pull Request，感謝您的使用和支持！

## 應用介面
![image](https://github.com/nicole27313864/ZH-Document-Conversion-Tool/assets/39577035/d1faf610-c91e-4366-b796-92c494b56460)
![image](https://github.com/nicole27313864/ZH-Document-Conversion-Tool/assets/39577035/2d50d6c2-5803-47e4-a749-c8dfc7919e6e)
