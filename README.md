# Auto-Reg-Mu: Tool Tự Động Đăng Ký Meta Muse AI (muse.ai)

Bộ công cụ tự động hóa đăng ký tài khoản **Meta Muse AI** (`https://muse.ai/`) hàng loạt từ danh sách Outlook OAuth2, tự động bóc tách mã xác nhận Meta (OTP) qua **cả IMAP XOAUTH2 lẫn Microsoft Graph API**, hỗ trợ xoay Proxy/4G, vượt cơ chế chống bot (Stealth Browser), phân loại kết quả chuẩn xác 3 tầng và tự động nạp phiên hoạt động vào pool `muse2api`.

---

## 🌟 Tính Năng Nổi Bật

1. **Auto Registration Thông Minh**:
   - Tự động điền email, gửi yêu cầu đăng ký lên Meta.
   - Đọc mã OTP 6 chữ số qua 2 đường song song (quét cả `Inbox` và `Junk/Spam`): IMAP XOAUTH2 trực tiếp (`outlook.office365.com`) và Microsoft Graph API (`/me/mailFolders/.../messages`). Chế độ `--otp-method auto` (mặc định) tự dùng đường nào token hỗ trợ — tài khoản dạng [IMAP/POP3/Graph] hay [GRAPH API] đều chạy; ép 1 đường bằng `--otp-method imap` hoặc `--otp-method graph`.
   - **Chỉ hỗ trợ email Outlook** (domain `outlook.*` như outlook.com, outlook.fr): tài khoản Hotmail/Live/MSN trong file đầu vào sẽ bị lọc bỏ.
   - Tự điền OTP bằng mô phỏng thao tác gõ tự nhiên (`press_sequentially`).
   - Tự động hoàn tất thông tin Profile (Họ tên, ngày sinh) hoặc điền mật khẩu nếu tài khoản Meta đã tồn tại.

2. **Hỗ Trợ 4G & Proxy Đa Dạng**:
   - **4G Điện Thoại (`--prompt-rotate`)**: Dừng nhắc người dùng gạt Bật/Tắt chế độ máy bay trên điện thoại để cấp IP 4G mới trước mỗi tài khoản.
   - **4G Proxy API (`--rotate-url`)**: Tự động gọi API URL để đổi IP của proxy 4G.
   - **Proxy đa định dạng (`--proxy`)**: Hỗ trợ `http://user:pass@ip:port`, `socks5://...`, `ip:port:user:pass`, `ip:port`.
   - **Xoay danh sách Proxy (`--proxy-file`)**: Tự luân phiên proxy cho từng tài khoản.

3. **Vượt Cơ Chế Chống Bot (Anti-Detection)**:
   - Sử dụng Google Chrome thật (`executable_path`).
   - Gỡ bỏ cờ tự động hóa (`AutomationControlled`, `navigator.webdriver = undefined`).
   - Thiết lập Viewport và User-Agent chuẩn thiết bị người dùng thật.

4. **Phân Loại Kết Quả 3 Tầng Triệt Để**:
   - `muse_success.txt` & `.json`: Tài khoản được cấp đầy đủ phiên hoạt động thực tế (`hatch_sess` + `hatch_vml`), VM assigned, không kẹt tại trang `/access`. Tự động nạp vào pool `muse2api`.
   - `muse_waitlist.txt` & `.json`: Tài khoản đã tạo Meta thành công nhưng Muse AI tạm xếp vào danh sách chờ (Waitlist) do IP bị chặn vị trí địa lý.
   - `muse_failed.txt` & `.json`: Tài khoản lỗi kỹ thuật (sai token, timeout OTP, ngắt kết nối).

5. **Công Cụ Bổ Trợ**:
   - `get_meta_otp.py`: CLI tra cứu nhanh mã OTP của một email bất kỳ.
   - `webmail_otp_server.py`: Giao diện Webmail cục bộ (cổng `8765`) hiển thị toàn bộ hòm thư và mã xác thực dạng trực quan giống tuan89.site.

---

## 📦 Cài Đặt

Yêu cầu: **Python 3.10+** và **Google Chrome** cài sẵn trên máy.

```bash
# 1. Clone repository
git clone https://github.com/mmmnhat/auto-reg-mu.git
cd auto-reg-mu

# 2. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# 3. Cài đặt browser binary cho Playwright
playwright install chromium
```

---

## 📋 Định Dạng File Đầu Vào

Chuẩn bị file tài khoản dạng văn bản `accounts.txt` (tham khảo `accounts.example.txt`):

```text
email|password|refresh_token|client_id
```
> Trong đó `client_id` mặc định của Mozilla Thunderbird OAuth2 là: `9e5f94bc-e8a4-4e73-b8be-63364c29d753`.
> Chỉ dùng email **Outlook** (`outlook.*`) — Hotmail không được hỗ trợ.

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Đăng ký tự động với mạng 4G điện thoại (Khuyên dùng)
Nếu bạn phát 4G từ điện thoại sang máy tính, sử dụng cờ `--prompt-rotate` để đổi IP sau mỗi tài khoản:
```bash
python auto_register_pool.py --file accounts.txt --prompt-rotate
```

### 2. Đăng ký qua Proxy (US Residential / Mobile Proxy)
```bash
python auto_register_pool.py --file accounts.txt --proxy "http://username:password@ip:port"
```
Hoặc xoay theo danh sách proxy:
```bash
python auto_register_pool.py --file accounts.txt --proxy-file proxies.txt
```

### 3. Đăng ký với Proxy 4G có API xoay IP
```bash
python auto_register_pool.py --file accounts.txt --proxy "http://ip:port" --rotate-url "https://api.proxy.com/change-ip" --rotate-wait 5
```

### 4. Mở cửa sổ trình duyệt trực quan (Head Mode)
Để quan sát toàn bộ quá trình tự động điền form trên màn hình:
```bash
python auto_register_pool.py --file accounts.txt --head --limit 5
```

### 5. Nạp tự động vào muse2api Pool
Thiết lập biến môi trường hoặc truyền tham số:
```bash
python auto_register_pool.py --file accounts.txt \
  --base "http://127.0.0.1:18610" \
  --key "m2a_your_key_here"
```

---

## 🛠️ Công Cụ Phụ Trợ

### Lấy nhanh mã OTP Meta từ Terminal:
```bash
python get_meta_otp.py your_account@outlook.com
python get_meta_otp.py --method graph your_account@outlook.com   # ép đọc qua Graph (auto|imap|graph)
```

### Khởi chạy máy chủ Webmail xem OTP trên trình duyệt:
```bash
python webmail_otp_server.py
```
Truy cập: `http://localhost:8765/mail/?email=your_account@outlook.com`

---

## 📄 Giấy Phép & Bảo Mật

- **Bảo mật**: Tuyệt đối không commit file chứa mật khẩu, Refresh Token hoặc dữ liệu cá nhân (`accounts.txt`, `data/`) lên kho mã nguồn.
- Giấy phép: MIT License.
