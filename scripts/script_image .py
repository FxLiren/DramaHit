# -*- coding: utf-8 -*-
import asyncio
import sqlite3
import sys
from playwright.async_api import async_playwright

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def run_full_crawler():
    async with async_playwright() as p:
        print("【正式版全量爬蟲】啟動中...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 封鎖靜態資源（圖片/CSS/字型），提升速度
        await page.route(
            "**/*.{png,jpg,jpeg,webp,svg,gif,css,woff,woff2}",
            lambda route: route.abort(),
        )

        # 初始化 SQLite 資料庫
        conn = sqlite3.connect("script_images.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS script_images")
        cursor.execute("""
            CREATE TABLE script_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_name TEXT,
                image_url TEXT
            )
        """)

        page_num = 1
        seen_scripts = set()  # 全域去重集合

        print("開始進行全站資料極速抓取...")
        while True:
            url = f"https://spot-point.com/scripts?page={page_num}"
            try:
                response = await page.goto(
                    url, wait_until="domcontentloaded", timeout=10000
                )
                if response and response.status != 200:
                    print(f"第 {page_num} 頁回應狀態碼異常 ({response.status})，停止抓取。")
                    break

                cards = await page.query_selector_all("a[href^='/scripts/']")
                if not cards:
                    print(f"第 {page_num} 頁已無卡片資料，爬取結束！")
                    break

                page_new_count = 0
                for card in cards:
                    img = await card.query_selector("img")
                    if not img:
                        continue

                    image_url = (await img.get_attribute("src")) or ""
                    script_name = (
                        (await img.get_attribute("alt"))
                        or (await card.inner_text())
                        or ""
                    ).strip()

                    script_name = script_name.split("\n")[0].strip()

                    # 核心去重機制：避免同一劇本重複存入
                    if not script_name or script_name in seen_scripts:
                        continue

                    if image_url:
                        if not image_url.startswith("http"):
                            image_url = f"https://spot-point.com{image_url}"

                        seen_scripts.add(script_name)
                        cursor.execute(
                            "INSERT INTO script_images (script_name, image_url) VALUES (?, ?)",
                            (script_name, image_url),
                        )
                        page_new_count += 1

                print(
                    f"第 {page_num} 頁完成 | 本頁新增: {page_new_count} 筆 | 總累計不重複: {len(seen_scripts)} 筆"
                )

                # 若連續存取但頁面不再提供新劇本，即完成全站讀取
                if page_new_count == 0 and page_num > 5:
                    print("已無新劇本資料，準備結束程序。")
                    break

                conn.commit()
                page_num += 1

            except Exception as e:
                print(f"讀取第 {page_num} 頁時結束或發生例外: {e}")
                break

        conn.commit()
        conn.close()
        await browser.close()
        print(f"\n恭喜！全量爬取完成，共存入 {len(seen_scripts)} 筆不重複劇本資料至 script_images.db")


if __name__ == "__main__":
    asyncio.run(run_full_crawler())