#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script chụp ảnh màn hình giao diện thực tế của 19 tài khoản trong muse_waitlist.json
sử dụng Playwright với cookie phiên làm việc qua Residential Proxy US.
"""

import asyncio
import json
import os
import secrets
import shutil
from typing import Dict, Any

from playwright.async_api import async_playwright

INPUT_JSON = "/Users/mmmnhat/Downloads/muse_waitlist.json"
OUTPUT_DIR = "/Users/mmmnhat/Downloads/muse_screenshots"
ARTIFACT_DIR = "/Users/mmmnhat/.gemini/antigravity/brain/4506d0ea-3761-4c7c-8f17-6feee583b48e/screenshots"

PROXY_HOST = "us2.cliproxy.io"
PROXY_PORT = 3010
PROXY_PASS = "jcgxzhbc"
PROXY_USER_BASE = "st7p1284504-region-US"


async def capture_account(sem: asyncio.Semaphore, idx: int, item: Dict[str, Any], p) -> Dict[str, Any]:
    async with sem:
        email = item.get("email", f"account_{idx}")
        clean_email = email.split("@")[0].replace(".", "_")
        cookies_dict = item.get("cookies", {})

        sid = f"shot_{secrets.token_hex(3)}"
        proxy_user = f"{PROXY_USER_BASE}-sid-{sid}-t-5"
        proxy_cfg = {
            "server": f"http://{PROXY_HOST}:{PROXY_PORT}",
            "username": proxy_user,
            "password": PROXY_PASS,
        }

        shot_filename = f"{idx:02d}_{clean_email}.png"
        out_path = os.path.join(OUTPUT_DIR, shot_filename)
        art_path = os.path.join(ARTIFACT_DIR, shot_filename)

        print(f"[{idx}/19] Bắt đầu chụp: {email} ...")
        context = None
        result = {
            "index": idx,
            "email": email,
            "file": shot_filename,
            "path": out_path,
            "art_path": art_path,
            "url": None,
            "title": None,
            "status": "pending"
        }

        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=f"/tmp/shot_prof_{clean_email}_{sid}",
                headless=True,
                proxy=proxy_cfg,
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                timezone_id="America/New_York",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ]
            )

            # Nạp cookie chuẩn RFC 6265bis (xử lý riêng tiền tố __Host-)
            playwright_cookies = []
            for k, v in cookies_dict.items():
                if k.startswith("__Host-"):
                    playwright_cookies.append({
                        "name": k,
                        "value": str(v),
                        "url": "https://muse.ai",
                        "secure": True
                    })
                else:
                    playwright_cookies.append({
                        "name": k,
                        "value": str(v),
                        "domain": ".muse.ai",
                        "path": "/"
                    })
            await context.add_cookies(playwright_cookies)

            page = context.pages[0] if context.pages else await context.new_page()

            # Mở muse.ai/thread/new để xem trạng thái chat/waitlist thực tế
            try:
                await page.goto("https://muse.ai/thread/new", wait_until="domcontentloaded", timeout=25000)
            except Exception:
                try:
                    await page.goto("https://muse.ai/", wait_until="domcontentloaded", timeout=20000)
                except Exception:
                    pass

            await asyncio.sleep(2.5)

            final_url = page.url
            title = await page.title()
            result["url"] = final_url
            result["title"] = title

            # Chụp màn hình
            await page.screenshot(path=out_path, full_page=False)
            shutil.copy2(out_path, art_path)
            result["status"] = "success"
            print(f"  [✓] Đã chụp thành công: {shot_filename} -> URL: {final_url}")

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"  [!] Lỗi khi chụp {email}: {e}")

        finally:
            if context:
                try:
                    await context.close()
                except Exception:
                    pass
                shutil.rmtree(f"/tmp/shot_prof_{clean_email}_{sid}", ignore_errors=True)

        return result


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data if isinstance(data, list) else list(data.values())
    total = len(items)
    print(f"[*] Tìm thấy {total} tài khoản trong {INPUT_JSON}. Bắt đầu chụp ảnh...")

    sem = asyncio.Semaphore(3)  # Chạy song song 3 worker để nhanh và không nghẽn proxy
    async with async_playwright() as p:
        tasks = [capture_account(sem, i + 1, item, p) for i, item in enumerate(items)]
        results = await asyncio.gather(*tasks)

    # Ghi manifest kết quả
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n==================================================")
    print(f"[*] HOÀN TẤT CHỤP {success_count}/{total} TÀI KHOẢN!")
    print(f"[*] Thư mục ảnh: {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
