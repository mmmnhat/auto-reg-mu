import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

json_path = os.environ.get("MUSE_WAITLIST_JSON", os.path.expanduser("~/Downloads/muse_waitlist.json"))
with open(json_path) as f:
    d = json.load(f)
items = d if isinstance(d, list) else list(d.values())
# Lấy acc 19 terryonjavaun hoặc acc đầu tiên
target_accs = [x for x in items if "terryon" in x.get("email", "")]
acc = target_accs[0] if target_accs else items[0]
email = acc["email"]
cookies_dict = acc["cookies"]

proxy_server = os.environ.get("PROXY_SERVER", "http://us2.cliproxy.io:3010")
proxy_user = os.environ.get("PROXY_USER", "")
proxy_pass = os.environ.get("PROXY_PASS", "")

proxy_cfg = {"server": proxy_server}
if proxy_user:
    proxy_cfg["username"] = proxy_user
    proxy_cfg["password"] = proxy_pass

async def main():
    print(f"[*] Đang khởi chạy Chromium trực quan cho tài khoản: {email}")
    async with async_playwright() as p:
        # headless=False để cửa sổ trình duyệt hiện lên màn hình Mac của bạn
        browser = await p.chromium.launch(
            headless=False,
            proxy=proxy_cfg,
            args=["--start-maximized", "--no-sandbox"]
        )
        ctx = await browser.new_context(
            viewport=None,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        
        # Nạp cookies phiên
        cookies = []
        for k, v in cookies_dict.items():
            if k.startswith("__Host-"):
                cookies.append({"name": k, "value": str(v), "url": "https://muse.ai", "secure": True})
            else:
                cookies.append({"name": k, "value": str(v), "domain": ".muse.ai", "path": "/"})
        await ctx.add_cookies(cookies)
        
        page = await ctx.new_page()
        
        # Bắt response để log ra terminal xem phản hồi khi bạn click
        page.on("response", lambda resp: print(f"  [NET {resp.status}] {resp.url[:80]}") if any(x in resp.url for x in ["auth", "check", "thread", "access"]) else None)
        
        print("-> Đang mở trang https://muse.ai/access/disclosure...")
        try:
            await page.goto("https://muse.ai/access/disclosure", wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"[!] Chú ý khi load: {e}")
            
        print("\n" + "="*60)
        print("🎉 TRÌNH DUYỆT ĐÃ MỞ TRÊN MÀN HÌNH MAC CỦA BẠN!")
        print("Bạn có thể bấm trực tiếp nút 'Get started' hoặc thao tác tùy ý.")
        print("Trình duyệt sẽ giữ nguyên cho đến khi bạn tự tắt cửa sổ.")
        print("="*60 + "\n")
        
        # Giữ cửa sổ mở cho tới khi người dùng đóng trình duyệt
        try:
            while len(ctx.pages) > 0 and not page.is_closed():
                await asyncio.sleep(1)
        except Exception:
            pass
        print("[*] Người dùng đã đóng trình duyệt.")

if __name__ == "__main__":
    asyncio.run(main())
