import csv
import datetime
import re
import sys
import time
from otp_mail import exchange_access_token, _outlook_rest_request

with open("UCTP6ae38202e259e_100.csv") as f:
    rows = list(csv.reader(f))

all_accounts = {}
for r in rows:
    if len(r) >= 2 and "|" in r[1]:
        parts = r[1].split("|")
        all_accounts[parts[0].strip()] = (parts[1].strip(), parts[2].strip(), parts[3].strip())

tokens = {}
seen_ids = set()

def get_token(email):
    pwd, rt, cid = all_accounts[email]
    if email in tokens:
        tok, exp = tokens[email]
        if time.time() < exp:
            return tok
    tok = exchange_access_token(rt, cid)
    tokens[email] = (tok, time.time() + 3000)
    return tok

start_cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)
print(f"[*] Đang theo dõi hòm thư. Chỉ bắt mail nhận sau {start_cutoff.isoformat()}...")
sys.stdout.flush()

while True:
    for email in list(all_accounts.keys())[:20]:
        try:
            tok = get_token(email)
            for folder in ["inbox", "junkemail"]:
                data = _outlook_rest_request(tok, f"/me/mailfolders/{folder}/messages", {
                    "$top": "3",
                    "$select": "Id,Subject,BodyPreview,ReceivedDateTime,From"
                })
                for msg in data.get("value", []):
                    mid = msg.get("Id")
                    if mid in seen_ids:
                        continue
                    seen_ids.add(mid)
                    
                    recv_str = msg.get("ReceivedDateTime", "")
                    if recv_str:
                        # Parse ISO 8601
                        recv_dt = datetime.datetime.fromisoformat(recv_str.replace("Z", "+00:00"))
                        if recv_dt < start_cutoff:
                            continue
                            
                    sender = msg.get("From", {}).get("EmailAddress", {}).get("Address", "")
                    subj = msg.get("Subject", "")
                    body = msg.get("BodyPreview", "")
                    
                    if any(k in (sender + subj).lower() for k in ["meta", "confirm", "security", "code"]):
                        match = re.search(r'\b\d{6}\b', subj + " " + body)
                        otp_code = match.group(0) if match else "Không rõ"
                        print(f"\n🎉 [ĐÃ CÓ MÃ OTP MỚI!]")
                        print(f"👉 TÀI KHOẢN:  {email}")
                        print(f"👉 MÃ OTP:     >>> {otp_code} <<<")
                        print(f"👉 TIÊU ĐỀ:    {subj}")
                        print(f"👉 THỜI GIAN:  {recv_str}")
                        print("="*60 + "\n")
                        sys.stdout.flush()
        except Exception:
            pass
    time.sleep(2)
