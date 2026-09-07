# -*- coding: utf-8 -*-
import asyncio
import re
import sqlite3
import sys
from playwright.async_api import async_playwright

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 併發數量設定 (建議 5-10)
CONCURRENCY_LIMIT = 8
DB_NAME = "script_meta.db"


async def block_unnecessary_resources(route):
    """僅封鎖大型媒體資源，保留 CSS/JS 正常渲染 DOM"""
    if route.request.resource_type in ["image", "font", "media"]:
        await route.abort()
    else:
        await route.continue_()


async def process_script_meta(semaphore, context, link, index, total, db_queue):
    """專門爬取 Part 2 屬性資料 + 封面圖片網址的 Task"""
    async with semaphore:
        page = await context.new_page()
        await page.route("**/*", block_unnecessary_resources)

        try:
            print(f"[{index}/{total}] 爬取中: {link}")
            await page.goto(
                link, wait_until="domcontentloaded", timeout=15000
            )

            # 1. 劇本名稱
            title_el = await page.query_selector("h1")
            script_name = (
                await title_el.inner_text() if title_el else "未知劇本"
            ).strip()

            # 2. 劇本封面圖片 URL 提取
            img_el = await page.query_selector("main img") or await page.query_selector("img")
            image_url = "無圖片"
            if img_el:
                src = await img_el.get_attribute("src") or await img_el.get_attribute("data-src")
                if src:
                    image_url = src if src.startswith("http") else f"https://spot-point.com{src}"

            # 3. 劇本類型
            type_els = await page.query_selector_all(
                ".badge, span.rounded-full, div.flex.gap-2 > span"
            )
            types = [await t.inner_text() for t in type_els]
            script_type = (
                " / ".join([t.strip() for t in types if t.strip()])
                if types
                else "未標示"
            )

            # 4. 內文全文提取 (優先抓 main，抓不到則備援 body)
            main_el = await page.query_selector("main")
            if main_el:
                page_text = await main_el.inner_text()
            else:
                body_el = await page.query_selector("body")
                page_text = await body_el.inner_text() if body_el else ""

            # 5. 正則匹配提取：時間 / 人數 / 評分
            time_match = re.search(
                r"(\d+(?:\.\d+)?\s*(?:小時|時|分鐘|分))", page_text
            )
            play_time = time_match.group(1).strip() if time_match else "未標示"

            player_match = re.search(
                r"(\d+[\d\s\-\~～男*女\(\)\（\）]*人)", page_text
            )
            players_count = (
                player_match.group(1).strip() if player_match else "未標示"
            )

            rating_match = re.search(r"(\b[1-9]\.\d\b)", page_text)
            rating = rating_match.group(1).strip() if rating_match else "未標示"

            # 推進資料庫寫入佇列 (包含 image_url)
            await db_queue.put(
                (script_name, image_url, script_type, players_count, play_time, rating)
            )

        except Exception as e:
            print(f"❌ 爬取 {link} 失敗: {e}")
        finally:
            await page.close()


async def db_writer(db_queue, db_name=DB_NAME):
    """獨立 SQLite 寫入程序，包含新增的 image_url 欄位"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS script_meta")
    cursor.execute("""
        CREATE TABLE script_meta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            script_name TEXT,
            image_url TEXT,
            script_type TEXT,
            players_count TEXT,
            play_time TEXT,
            rating TEXT
        )
    """)

    count = 0
    while True:
        data = await db_queue.get()
        if data is None:  # 結束標籤
            break

        cursor.execute(
            """
            INSERT INTO script_meta (script_name, image_url, script_type, players_count, play_time, rating)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            data,
        )
        count += 1
        if count % 20 == 0:
            conn.commit()

        db_queue.task_done()

    conn.commit()
    conn.close()


async def main():
    async with async_playwright() as p:
        print("🚀 【Part 2 + 封面圖片 全量爬取】啟動瀏覽器中...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # 1. 遍歷全站列表頁收集連結
        page = await context.new_page()
        await page.route("**/*", block_unnecessary_resources)

        all_script_links = set()
        page_num = 1
        print("正在收集全站劇本連結...")

        while True:
            url = f"https://spot-point.com/scripts?page={page_num}"
            try:
                response = await page.goto(
                    url, wait_until="domcontentloaded", timeout=15000
                )
                if response and response.status != 200:
                    break

                links = await page.eval_on_selector_all(
                    "a[href^='/scripts/']",
                    "elements => elements.map(e => e.href)",
                )
                valid_links = [
                    l for l in links if l != "https://spot-point.com/scripts"
                ]
                new_links = [
                    l for l in valid_links if l not in all_script_links
                ]

                if not new_links:
                    print(f"第 {page_num} 頁無新資料，連結收集完畢。")
                    break

                for l in new_links:
                    all_script_links.add(l)

                print(
                    f"第 {page_num} 頁收集完成，累計取得 {len(all_script_links)} 筆劇本。"
                )
                page_num += 1
            except Exception as e:
                print(f"收集列表頁 {page_num} 結束或出錯: {e}")
                break

        await page.close()

        script_list = list(all_script_links)
        total_scripts = len(script_list)
        print(f"\n🔥 共收集到 {total_scripts} 筆劇本，開始高併發爬取 (含圖片連結)...")

        # 2. 啟動 Task 與佇列
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        db_queue = asyncio.Queue()

        writer_task = asyncio.create_task(db_writer(db_queue))

        tasks = [
            process_script_meta(
                semaphore, context, link, idx, total_scripts, db_queue
            )
            for idx, link in enumerate(script_list, 1)
        ]

        await asyncio.gather(*tasks)

        # 結束佇列並關閉
        await db_queue.put(None)
        await writer_task

        await browser.close()
        print(
            f"\n🎉 含有圖片網址的 Part 2 全量爬取完畢！資料已成功寫入：{DB_NAME}"
        )


if __name__ == "__main__":
    asyncio.run(main())