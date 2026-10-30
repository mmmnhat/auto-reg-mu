# Auto-Reg-Mu: Tool Tự Động Đăng Ký Meta Muse AI (muse.ai)

Bộ công cụ tự động hóa toàn diện quy trình đăng ký tài khoản **Meta Muse AI** (`https://muse.ai/`) hàng loạt từ danh sách Outlook/Hotmail OAuth2, tự động bóc tách mã xác nhận Meta (OTP) siêu tốc qua **Outlook REST API v2.0**, hỗ trợ xoay Proxy Dân cư / Mobile 4G T-Mobile, cô lập Profile chống chết chùm (Isolated Clean Profile), phân loại kết quả chuẩn xác và hỗ trợ nạp thẳng vào pool `muse2api`.

---

## 🌟 Tính Năng & Điểm Nổi Bật

1. **Đăng Ký Tự Động 100% (High-Performance Engine)**:
   - Tự động điền email, gửi yêu cầu đăng ký lên Meta.
   - Đọc mã OTP 6 số tự động từ hòm thư qua **Outlook REST API v2.0** trong 15–30 giây (quét cả `Inbox` và `Junk/Spam`), áp dụng bộ lọc thời gian thực triệt tiêu 100% mã OTP cũ.
   - Tự động điền Họ tên chuẩn tự nhiên (loại bỏ hoàn toàn các tiền tố/hậu tố bị Meta cấm như `"AI"`, `"Bot"`).
   - Tự động điền Ngày sinh (>21 tuổi) tương thích với form Radix UI combobox của Meta.
   - Tự động nhận diện và click nút **"Get started"** tại màn hình Onboarding Disclosure (`/access/disclosure`).
   - Tự động xác thực quyền tạo video bằng lệnh kiểm tra thực tế: *"Muse vẫy tay chào thân thiện"*.

2. **Cơ Chế Chống Phát Hiện & Cách Ly Hồ Sơ (Anti-Detection)**:
   - **Isolated Clean Profile**: Mỗi tài khoản chạy trong một thư mục Profile độc lập (`/tmp/muse_prof_*`), không chia sẻ cache/cookies, chống chết chùm tài khoản.
   - **Canvas & WebGL Spoofing**: Bơm vi nhiễu (micro-noise) vào Canvas Context và giả lập card đồ họa NVIDIA để mỗi luồng có một Fingerprint độc nhất.
   - **Xóa cờ tự động hóa**: Mock đầy đủ `window.chrome`, gỡ bỏ `navigator.webdriver`.

3. **Hỗ Trợ Mạng & Xoay Proxy Linh Hoạt**:
   - **Proxy đa giao thức**: Hỗ trợ `http://host:port`, `socks5://...`, `host:port:user:pass`, `http://user:pass@host:port`.
   - **Proxy Dân Cư Cliproxy**: Tự động sinh `sid` sticky session độc lập theo từng tài khoản.
   - **Proxy 4G Mobile (ProxyTower, T-Mobile US)**: Hỗ trợ gọi URL đổi IP tự động (`--rotate-url`).
   - **Đa luồng (`-c` / `--concurrency`)**: Chạy song song nhiều trình duyệt độc lập.

4. **Phân Loại Kết Quả 3 Tầng Triệt Để**:
   - `muse_success.txt` / `.json`: Tài khoản hoạt động 100%, có `hatch_vml`, vượt qua bài test tạo video thật.
   - `muse_waitlist.txt` / `.json`: Tài khoản Meta đã tạo thành công, có cookie `hatch_sess`, sẵn sàng kích hoạt khi Meta mở đợt duyệt.
   - `muse_failed.txt` / `.json`: Tài khoản lỗi kỹ thuật (timeout OTP, mạng rớt, từ chối đăng ký) kèm lý do chi tiết.

---

## 📁 Cấu Trúc Dự Án & Các Công Cụ

| Tệp tin | Vai trò / Công dụng |
|---|---|
| **`auto_register_pool.py` / `main.py`** | **Engine chính:** Chạy đăng ký tự động hàng loạt, hỗ trợ proxy xoay, đa luồng, nạp pool `muse2api`. |
| **`otp_mail.py`** | **Module OTP:** Đọc mã xác thực qua Outlook REST API v2.0, Microsoft Graph API và IMAP XOAUTH2. |
| **`watch_live_otp.py`** | **Giám sát OTP Real-time:** Tool túc trực quét liên tục toàn bộ hòm thư, hễ có mail Meta gửi về là in mã to ra màn hình. |
| **`local_bridge.py`** | **Cầu nối Proxy cho iPhone/iPad (Port 8899):** Chuyển tiếp proxy US cho iOS mà không bị lỗi đứt mạng của Apple. |
| **`open_browser_manual.py`** | **Mở trình duyệt trực quan:** Mở Chromium có sẵn session cookie để kiểm tra thao tác bằng tay. |
| **`capture_waitlist_screens.py`** | **Chụp ảnh màn hình hàng loạt:** Tự động đăng nhập vào 19+ tài khoản và chụp ảnh trạng thái lưu vào thư mục. |
| **`webmail_otp_server.py`** | **Web UI Hòm thư (Port 8765):** Giao diện web xem email trực quan tương tự `tuan89.site`. |
| **`report.md`** | **Báo cáo kỹ thuật:** Đánh giá chuyên sâu về cơ chế chống bot, cổng kích hoạt thẻ và ứng dụng native của Meta. |

---

## 📦 Cài Đặt Môi Trường

Yêu cầu: **Python 3.10+** (khuyên dùng Python 3.11 hoặc 3.12).

```bash
# 1. Clone repository
git clone https://github.com/mmmnhat/auto-reg-mu.git
cd auto-reg-mu

# 2. Tạo virtual environment và kích hoạt
python3 -m venv .venv
source .venv/bin/activate

# 3. Cài đặt các gói phụ thuộc
pip install -r requirements.txt

# 4. Cài đặt Chromium cho Playwright
playwright install chromium
```

---

## 📋 Định Dạng File Đầu Vào

Tool hỗ trợ cả 2 định dạng file danh sách tài khoản:

### Định dạng 1: File CSV (Chuẩn đại lý / tool bán acc)
File `UCTP..._100.csv`:
```csv
"UID"
"email@outlook.com","email@outlook.com|password|refresh_token|client_id","date","note"
```

### Định dạng 2: File TXT (Mỗi dòng 1 tài khoản)
File `accounts.txt`:
```text
email@outlook.com|password|refresh_token|client_id
```
> Client ID mặc định của Mozilla Thunderbird OAuth2: `9e5f94bc-e8a4-4e73-b8be-63364c29d753`.

---

## 🚀 Hướng Dẫn Vận Hành

### 1. Chạy đăng ký tự động đơn luồng (Cơ bản)
```bash
python main.py \
  --file UCTP6ae38202e259e_100.csv \
  --proxy "http://username:password@us2.cliproxy.io:3010" \
  --start 0 \
  --limit 5
```

### 2. Chạy với Proxy 4G Mobile xoay IP (ProxyTower / T-Mobile)
```bash
python main.py \
  --file UCTP6ae38202e259e_100.csv \
  --proxy "http://username:password@gateway.proxytower.io:1080" \
  --rotate-url "https://proxytower.io/r/YOUR_KEY/random" \
  --rotate-wait 15 \
  --start 10 \
  --limit 5
```

### 3. Chạy đa luồng song song (Tăng tốc tối đa)
```bash
python main.py \
  --file UCTP6ae38202e259e_100.csv \
  --proxy "http://username:password@us2.cliproxy.io:3010" \
  -c 3 \
  --limit 30
```

### 4. Mở cửa sổ trực quan để theo dõi (Head Mode)
Thêm cờ `--head` để xem trực tiếp các thao tác điền form trên màn hình:
```bash
python main.py --file UCTP6ae38202e259e_100.csv --head --limit 1
```

### 5. Tự động nạp vào Pool `muse2api`
```bash
python main.py \
  --file UCTP6ae38202e259e_100.csv \
  --proxy "http://..." \
  --base "http://127.0.0.1:18610" \
  --key "m2a_sec_chupoolacc2026"
```

---

## 🛠️ Hướng Dẫn Sử Dụng Các Tool Bổ Trợ

### 1. Túc trực bắt mã OTP Real-time (`watch_live_otp.py`)
Khi bạn cần đăng nhập tài khoản trên điện thoại hoặc trình duyệt ngoài và muốn lấy mã OTP ngay lập tức:
```bash
python watch_live_otp.py
```
> Script sẽ quét liên tục hòm thư của toàn bộ 100 tài khoản. Hễ bạn bấm gửi OTP trên web/app, mã 6 số sẽ in nổi bật ngay trên Terminal trong vòng 2-3 giây.

### 2. Phát Proxy US cho iPhone/iPad không bị lỗi mạng (`local_bridge.py`)
iOS có lỗi bảo mật với proxy Wi-Fi có mật khẩu. Chạy script này trên máy tính để tạo cổng chuyển tiếp nội bộ:
```bash
python local_bridge.py
```
* **Cài đặt trên iPhone:** Vào Wi-Fi $\rightarrow$ Định cấu hình Proxy $\rightarrow$ **Thủ công (Manual)**:
  * Máy chủ: `IP_MÁY_TÍNH` (VD: `192.168.0.235`)
  * Cổng: `8899`
  * Xác thực: **TẮT** (Off)
* iPhone sẽ vào mạng bình thường với địa chỉ IP Mỹ 100%.

### 3. Mở nhanh trình duyệt kèm phiên tài khoản có sẵn (`open_browser_manual.py`)
```bash
python open_browser_manual.py
```
> Trình duyệt Chromium sẽ tự động mở lên, nạp sẵn cookies của tài khoản trong `muse_waitlist.json` để bạn thao tác trực tiếp.

### 4. Chụp ảnh minh chứng toàn bộ tài khoản Waitlist (`capture_waitlist_screens.py`)
```bash
python capture_waitlist_screens.py
```
> Tự động đăng nhập vào toàn bộ danh sách tài khoản trong `muse_waitlist.json` và lưu ảnh chụp trang màn hình vào `~/Downloads/muse_screenshots/`.

---

## 🔒 Lưu Ý Về Chính Sách Của Meta Muse AI

1. **Về việc đòi thẻ ngân hàng (`/access/verification`):**
   * Nếu đăng ký bằng IP proxy dùng chung (High Fraud Score), Meta sẽ chuyển hướng sang trang xác minh thẻ Visa/MasterCard.
   * **Khuyến nghị:** Sử dụng Proxy 4G Mobile sạch (như T-Mobile US) hoặc thuê SIM ảo nhận SMS OTP số Mỹ (+1) để không bị yêu cầu thẻ.
2. **Về ứng dụng Mobile:**
   * Ứng dụng chính thức là **"Muse from Meta"** (Bundle ID: `com.facebook.hatch`) trên Apple iOS App Store (ID: `6760173601`).
   * Ứng dụng dùng cơ chế phần cứng Apple DeviceCheck để xác thực danh tính.

---

## 📄 Bản Quyền & Giấy Phép

Phát triển bởi đội ngũ MuLon / mmmnhat. Giấy phép sử dụng nội bộ MIT License.
