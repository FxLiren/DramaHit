# 探劇實錄 DramaHit

「探劇實錄」是一個以劇本殺為主題的 Django 網站專題，提供劇本資訊瀏覽、搜尋、排行榜與推薦，以及會員相關功能。

本專案為團隊協作開發作品，使用 Django 作為後端框架，搭配 HTML、CSS、JavaScript 製作網頁介面，並使用 SQLite 儲存相關資料。

---

## 專案功能

### 首頁
- 提供網站主要功能入口
- 顯示劇本及推薦內容
- 可透過導覽功能前往網站各主要頁面

### 劇本資訊
- 瀏覽劇本列表
- 查看劇本詳細資訊
- 劇本搜尋及相關資料呈現

### 排行榜與推薦
- 顯示劇本排行榜
- 提供劇本推薦內容

### 會員系統
- 會員註冊
- 會員登入與登出
- Email 信箱驗證
- 忘記密碼與密碼重設
- 會員中心
- 我的收藏
- 瀏覽歷史紀錄

---

## 使用技術

**後端**
- Python 3.12
- Django 6.1

**前端**
- HTML
- CSS
- JavaScript
- Responsive Web Design（RWD）

**資料庫**
- SQLite

**其他**
- Git / GitHub
- Gmail SMTP
- python-dotenv

---

## 專案結構

```text
DramaHit/
├── account/             # 會員相關功能
├── config/              # Django 專案設定
├── home/                # 首頁
├── recommendation/      # 排行榜與推薦
├── script/              # 劇本相關功能
├── scripts/             # 專案相關腳本
├── static/              # CSS、JavaScript、圖片及相關資料
├── templates/           # 共用網頁模板
├── .env.example         # 環境變數設定範例
├── db.sqlite3           # SQLite 資料庫
├── manage.py            # Django 管理程式
└── requirements.txt     # Python 套件清單
```

---

## 安裝與執行

### 1. 建立虛擬環境

建議使用 Python 3.12。

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. 安裝所需套件

```powershell
pip install -r requirements.txt
```

### 3. 設定環境變數

本專案使用 `.env` 儲存 Email 寄信功能所需的環境變數。

專案內提供 `.env.example` 作為設定範例。首次執行專案時，請將 `.env.example` 複製一份並重新命名為 `.env`：

```text
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

請將內容替換為自己的 Gmail 帳號與 Google 應用程式密碼。

`.env` 已加入 `.gitignore`，不會上傳至 GitHub；`.env.example` 僅用於說明專案需要的環境變數，不包含實際帳號或密碼。

### 4. 執行 Django

```powershell
python manage.py runserver
```

啟動成功後，在瀏覽器開啟：

```text
http://127.0.0.1:8000/
```

即可進入網站。

---

## 會員系統說明

會員系統使用 Django 內建的 User 模型及驗證機制進行開發。

### 會員註冊與 Email 驗證

使用者完成註冊後，帳號會先設定為未啟用狀態。

系統透過 Gmail SMTP 寄送驗證信，並利用 Django Token 產生驗證連結。使用者點擊連結且驗證成功後，系統才會將帳號啟用。

另外針對使用者輸入錯誤 Email、未完成驗證的情況加入處理機制，避免未驗證帳號持續占用相同的 Username。

### 登入與會員中心

完成 Email 驗證的會員可以登入系統，並在會員中心查看會員相關資訊及使用會員限定功能。

### 密碼重設

忘記密碼時，可以透過註冊 Email 取得密碼重設連結，並設定新的登入密碼。

### 收藏功能

登入會員可以收藏感興趣的劇本，並透過會員功能查看自己的收藏內容。

### 瀏覽歷史

系統會記錄會員瀏覽過的劇本及瀏覽時間。

再次瀏覽相同劇本時會更新該筆紀錄的瀏覽時間，歷史紀錄頁面顯示最近 15 筆瀏覽紀錄。

---

## 團隊協作

本專案為團隊專題作品，開發過程使用 Git 與 GitHub 進行版本控制及程式碼整合。

專案功能分為首頁、劇本資訊、排行榜與推薦、會員系統等部分，由團隊成員分工完成後整合至 Django 專案。

---

## 個人負責內容

本人主要負責會員系統相關功能的開發與整合，包括：

- 會員註冊、登入與登出
- Email 驗證流程
- 忘記密碼與密碼重設
- 會員中心
- 會員收藏功能整合
- 瀏覽歷史紀錄
- 會員相關頁面的 RWD 調整

開發過程中亦針對實際測試發現的問題進行修正，例如未完成 Email 驗證的帳號占用 Username、郵件寄送失敗時的帳號處理，以及瀏覽歷史紀錄的顯示方式等。

透過本專題實際練習 Django 網站開發、會員驗證流程、資料庫操作、Email 寄送，以及 Git/GitHub 團隊協作與版本控制。