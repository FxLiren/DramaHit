# -*- coding: utf-8 -*-
import asyncio
import sqlite3
import sys
from playwright.async_api import async_playwright

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def run_part1_full():
    async with async_playwright() as p:
        print("【Part 1 正式爬取】啟動瀏覽器中...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. 自動遍歷所有列表頁收集所有劇本 URL
        all_script_links = set()
        page_num = 1

        print("正在收集所有劇本連結...")
        while True:
            url = f"https://spot-point.com/scripts?page={page_num}"
            try:
                response = await page.goto(
                    url, wait_until="domcontentloaded", timeout=15000
                )
                if response and response.status != 200:
                    break

                await page.wait_for_timeout(400)
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
                    print(f"第 {page_num} 頁無新資料，收集完畢。")
                    break

                for l in new_links:
                    all_script_links.add(l)

                print(
                    f"第 {page_num} 頁收集完成，目前累計 {len(all_script_links)} 筆劇本。"
                )
                page_num += 1

            except Exception as e:
                print(f"讀取列表頁 {page_num} 結束或出錯: {e}")
                break

        script_list = list(all_script_links)
        print(f"\n共收集到 {len(script_list)} 筆劇本，開始抓取詳細資料...")

        # 2. 初始化正式資料庫 script_info.db
        conn = sqlite3.connect("script_info.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS script_info")
        cursor.execute("""
            CREATE TABLE script_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_name TEXT,
                description TEXT,
                shop_name TEXT,
                official_site TEXT,
                ig_url TEXT,
                fb_url TEXT
            )
        """)

        # 3. 逐頁爬取詳情與店家資訊
        for index, link in enumerate(script_list, 1):
            try:
                print(f"[{index}/{len(script_list)}] 爬取中: {link}")
                await page.goto(
                    link, wait_until="domcontentloaded", timeout=15000
                )
                await page.wait_for_timeout(500)

                # A. 劇本名稱
                title_el = await page.query_selector("h1")
                script_name = (
                    await title_el.inner_text() if title_el else "未知劇本"
                ).strip()

                # B. 劇本簡介
                desc_el = await page.query_selector(
                    "main p"
                ) or await page.query_selector(".leading-relaxed")
                description = (
                    await desc_el.inner_text() if desc_el else "無簡介"
                ).strip()

                # C. 店家資訊
                studio_elements = await page.query_selector_all(
                    "a[href*='/studios/']"
                )

                found_shops = []
                processed_studio_urls = set()

                for s_elem in studio_elements:
                    href = await s_elem.get_attribute("href")
                    if not href or href in processed_studio_urls:
                        continue

                    processed_studio_urls.add(href)

                    card_handle = await s_elem.evaluate_handle(
                        """el => {
                        let cur = el;
                        while (cur && cur.tagName !== 'BODY') {
                            if (cur.innerText && (cur.innerText.includes('預約') || cur.innerText.includes('Instagram') || cur.innerText.includes('Facebook'))) {
                                return cur;
                            }
                            cur = cur.parentElement;
                        }
                        return el.parentElement;
                    }"""
                    )

                    card_node = card_handle.as_element()
                    shop_name = "未知店家"
                    if card_node:
                        lines = [
                            l.strip()
                            for l in (await card_node.inner_text()).split("\n")
                            if l.strip()
                        ]
                        clean_lines = [
                            l
                            for l in lines
                            if l
                            not in [
                                "預約",
                                "立即預約",
                                "查看預約",
                                "Instagram",
                                "Facebook",
                            ]
                            and not l.startswith("開設店家")
                        ]
                        if clean_lines:
                            shop_name = clean_lines[0]

                    studio_full_url = (
                        href
                        if href.startswith("http")
                        else f"https://spot-point.com{href}"
                    )
                    
                    official_site = "無資料"
                    ig_url = "無資料"
                    fb_url = "無資料"

                    studio_page = await context.new_page()
                    try:
                        await studio_page.goto(
                            studio_full_url,
                            wait_until="domcontentloaded",
                            timeout=10000,
                        )
                        await studio_page.wait_for_timeout(500)

                        all_anchors = await studio_page.query_selector_all("a[href]")
                        for a in all_anchors:
                            a_href = (await a.get_attribute("href") or "").strip()
                            a_text = (await a.inner_text() or "").strip().lower()

                            if a_href.startswith("http") and "spot-point.com" not in a_href:
                                if "instagram.com" in a_href.lower() or "ig" in a_text:
                                    if ig_url == "無資料":
                                        ig_url = a_href
                                elif "facebook.com" in a_href.lower() or "fb" in a_text or "臉書" in a_text:
                                    if fb_url == "無資料":
                                        fb_url = a_href
                                elif "官網" in a_text or "website" in a_href.lower() or "official" in a_href.lower():
                                    if official_site == "無資料":
                                        official_site = a_href
                                else:
                                    if official_site == "無資料":
                                        official_site = a_href

                    except Exception as err:
                        print(f"  └ 進入工作室頁面抓取失敗: {err}")
                    finally:
                        await studio_page.close()

                    found_shops.append((shop_name, official_site, ig_url, fb_url))

                if found_shops:
                    for s_name, off_site, ig, fb in found_shops:
                        cursor.execute(
                            """
                            INSERT INTO script_info (script_name, description, shop_name, official_site, ig_url, fb_url)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """,
                            (script_name, description, s_name, off_site, ig, fb),
                        )
                else:
                    cursor.execute(
                        """
                        INSERT INTO script_info (script_name, description, shop_name, official_site, ig_url, fb_url)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (script_name, description, "無關聯店家", "無資料", "無資料", "無資料"),
                    )

                if index % 10 == 0:
                    conn.commit()

            except Exception as e:
                print(f"爬取 {link} 失敗: {e}")

        conn.commit()
        conn.close()
        await browser.close()
        print("\nPart 1 全量爬取完成！所有資料已寫入 script_info.db")


if __name__ == "__main__":
    asyncio.run(run_part1_full())