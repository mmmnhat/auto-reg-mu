#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tool CLI lấy mã OTP từ Meta nhanh cho một email bất kỳ trong file.

Cách dùng:
    python get_meta_otp.py user@hotmail.com
    python get_meta_otp.py --file accounts.txt user@hotmail.com
"""

import argparse
import email
import imaplib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request


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


def get_otp(acc):
    token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    token_data = urllib.parse.urlencode({
        "client_id": acc["client_id"],
        "grant_type": "refresh_token",
        "refresh_token": acc["refresh_token"],
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=token_data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            access_token = data.get("access_token")
    except Exception as e:
        print(f"[!] Lỗi đổi OAuth2 access token: {e}")
        return None, None, None

    auth_string = f"user={acc['email']}\x01auth=Bearer {access_token}\x01\x01".encode("utf-8")
    try:
        mail = imaplib.IMAP4_SSL("outlook.office365.com", 993, timeout=15)
        mail.authenticate("XOAUTH2", lambda x: auth_string)
    except Exception as e:
        print(f"[!] Lỗi kết nối IMAP XOAUTH2: {e}")
        return None, None, None

    print(f"[*] Đang quét hòm thư {acc['email']}...")
    for folder in ["Inbox", "Junk"]:
        try:
            status, _ = mail.select(folder)
            if status != "OK":
                continue
            status, messages = mail.search(None, "ALL")
            mids = messages[0].split()
            for mid in reversed(mids[-4:]):
                res, msg_data = mail.fetch(mid, "(RFC822)")
                if res != "OK" or not msg_data or not msg_data[0]:
                    continue
                msg = email.message_from_bytes(msg_data[0][1])
                frm = msg.get("From", "")
                subj = msg.get("Subject", "")

                if any(k in frm or k in subj for k in ["Meta", "meta.com", "Xác nhận", "Confirm", "code", "Mã"]):
                    raw_content = ""
                    for part in msg.walk():
                        if part.get_content_type() in ["text/html", "text/plain"]:
                            raw_content += part.get_payload(decode=True).decode(errors="ignore")

                    m = re.search(r"Mã xác nhận\s+(\d{6})", raw_content)
                    if m:
                        try: mail.logout()
                        except Exception: pass
                        return m.group(1), frm, subj

                    m2 = re.search(r"letter-spacing:[^>]*>(\d{6})<", raw_content)
                    if m2:
                        try: mail.logout()
                        except Exception: pass
                        return m2.group(1), frm, subj

                    candidates = re.findall(r"\b\d{6}\b", raw_content)
                    for c in candidates:
                        if c not in ("141823", "000000", "123456"):
                            try: mail.logout()
                            except Exception: pass
                            return c, frm, subj
        except Exception:
            pass

    try:
        mail.logout()
    except Exception:
        pass
    return None, None, None


def main():
    parser = argparse.ArgumentParser(description="Tool CLI lấy mã OTP từ Meta nhanh cho một Hotmail bất kỳ.")
    parser.add_argument("email", help="Email cần lấy OTP")
    parser.add_argument("--file", default=os.environ.get("MUSE_ACCOUNTS_FILE", "accounts.txt"), help="File txt danh sách acc")
    args = parser.parse_args()

    acc = find_account(args.email, args.file)
    if not acc:
        print(f"[!] Không tìm thấy tài khoản khớp với: '{args.email}' trong {args.file}")
        sys.exit(1)

    print(f"[✓] Tìm thấy tài khoản: {acc['email']}")
    otp, frm, subj = get_otp(acc)
    if otp:
        print("\n" + "=" * 40)
        print(f"👉 MÃ OTP META:  {otp}")
        print("=" * 40)
        print(f"Từ:      {frm}")
        print(f"Tiêu đề: {subj}")
    else:
        print("\n[!] Không tìm thấy thư OTP mới từ Meta trong Inbox và Junk.")


if __name__ == "__main__":
    main()
