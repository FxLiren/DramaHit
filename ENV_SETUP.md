\# 環境變數設定說明



本專案的 Email 寄信功能使用環境變數保存 Gmail SMTP 所需的帳號資訊。



為避免將實際帳號及應用程式密碼上傳至 GitHub，專案不提供實際使用的 `.env`，而是提供 `.env.example` 作為設定範例。



\## 設定方式



1\. 將專案根目錄中的 `.env.example` 複製一份。

2\. 將複製後的檔案重新命名為 `.env`。

3\. 修改 `.env` 中的內容：



```text

GMAIL\_EMAIL=your\_email@gmail.com

GMAIL\_APP\_PASSWORD=your\_app\_password

