#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tool CLI lấy mã OTP từ Meta nhanh cho một email Outlook bất kỳ trong file.

Đọc OTP qua cả IMAP XOAUTH2 và Microsoft Graph (module otp_mail dùng chung).
CHỈ hỗ trợ email Outlook (outlook.*) — khớp với auto_register_pool.py.

Cách dùng:
    python get_meta_otp.py user@outlook.com
    python get_meta_otp.py --file accounts.txt user@outlook.com
    python get_meta_otp.py --method graph user@outlook.com   # ép 1 đường: auto|imap|graph
"""

import argparse
import os
import sys

from otp_mail import is_outlook_email, poll_meta_otp_detailed


def find_account(email_query: str, filepath: str):
    if not os.path.isfile(filepath):
        print(f"[!] Không tìm thấy file dữ liệu: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip() or "|" not in line:
                continue
            parts = line.strip().split("|")
            if len(parts) >= 4 and email_query.lower() in parts[0].strip().lower():
                return {
                    "email": parts[0].strip(),
                    "pwd": parts[1].strip(),
                    "refresh_token": parts[2].strip(),
                    "client_id": parts[3].strip(),
                }
    return None


def main():
    parser = argparse.ArgumentParser(description="Tool CLI lấy mã OTP từ Meta nhanh cho một Outlook bất kỳ (IMAP + Graph).")
    parser.add_argument("email", help="Email cần lấy OTP")
    parser.add_argument("--file", default=os.environ.get("MUSE_ACCOUNTS_FILE", "accounts.txt"), help="File txt danh sách acc")
    parser.add_argument("--method", choices=["auto", "imap", "graph"], default=os.environ.get("MUSE_OTP_METHOD", "auto"),
                        help="Đường đọc OTP: auto = cả IMAP + Graph (mặc định), imap, graph")
    parser.add_argument("--timeout", type=int, default=30, help="Số giây chờ quét thư (mặc định 30)")
    args = parser.parse_args()

    acc = find_account(args.email, args.file)
    if not acc:
        print(f"[!] Không tìm thấy tài khoản khớp với: '{args.email}' trong {args.file}")
        sys.exit(1)

    if not is_outlook_email(acc["email"]):
        print(f"[!] '{acc['email']}' không phải email Outlook — tool chỉ hỗ trợ outlook.* (bỏ qua Hotmail/Live/MSN).")
        sys.exit(1)

    print(f"[✓] Tìm thấy tài khoản: {acc['email']}")
    print(f"[*] Đang quét hòm thư (method={args.method}: IMAP + Graph)...")
    # start_timestamp=0: lấy cả thư OTP đã có sẵn trong hộp thư, không chỉ thư mới
    hit = poll_meta_otp_detailed(acc["email"], acc["refresh_token"], acc["client_id"], 0, args.timeout, args.method)
    if hit:
        otp, frm, subj = hit
        print("\n" + "=" * 40)
        print(f"👉 MÃ OTP META:  {otp}")
        print("=" * 40)
        print(f"Từ:      {frm}")
        print(f"Tiêu đề: {subj}")
    else:
        print("\n[!] Không tìm thấy thư OTP mới từ Meta trong Inbox và Junk (cả IMAP lẫn Graph).")


if __name__ == "__main__":
    main()
