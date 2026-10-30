import argparse
import asyncio
import base64
import os
import sys

UPSTREAM_HOST = os.environ.get("UPSTREAM_PROXY_HOST", "us2.cliproxy.io")
UPSTREAM_PORT = int(os.environ.get("UPSTREAM_PROXY_PORT", "3010"))
UPSTREAM_USER = os.environ.get("UPSTREAM_PROXY_USER", "")
UPSTREAM_PASS = os.environ.get("UPSTREAM_PROXY_PASS", "")
LOCAL_PORT = int(os.environ.get("LOCAL_BRIDGE_PORT", "8899"))

auth_token = base64.b64encode(f"{UPSTREAM_USER}:{UPSTREAM_PASS}".encode()).decode() if UPSTREAM_USER else ""

async def pipe(reader, writer):
    try:
        while not reader.at_eof():
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except Exception:
        pass
    finally:
        writer.close()

async def handle_client(client_reader, client_writer):
    try:
        # Đọc request đầu tiên từ iPhone
        req_line = await client_reader.readline()
        if not req_line:
            client_writer.close()
            return
            
        parts = req_line.decode('latin1').split()
        if len(parts) < 2:
            client_writer.close()
            return
            
        method, target = parts[0], parts[1]
        
        # Đọc headers còn lại
        headers = []
        while True:
            line = await client_reader.readline()
            if not line or line == b'\r\n' or line == b'\n':
                break
            headers.append(line)

        # Mở kết nối tới Upstream Cliproxy
        up_reader, up_writer = await asyncio.open_connection(UPSTREAM_HOST, UPSTREAM_PORT)
        
        if method.upper() == "CONNECT":
            # HTTPS Tunneling
            connect_req = (
                f"CONNECT {target} HTTP/1.1\r\n"
                f"Host: {target}\r\n"
                f"Proxy-Authorization: Basic {auth_token}\r\n"
                f"Proxy-Connection: Keep-Alive\r\n\r\n"
            ).encode()
            up_writer.write(connect_req)
            await up_writer.drain()
            
            # Đọc phản hồi 200 Connection established từ Cliproxy
            up_resp = await up_reader.readline()
            while True:
                line = await up_reader.readline()
                if not line or line == b'\r\n' or line == b'\n':
                    break
            
            if b"200" in up_resp:
                client_writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                await client_writer.drain()
                # Nối luồng dữ liệu 2 chiều
                asyncio.create_task(pipe(client_reader, up_writer))
                asyncio.create_task(pipe(up_reader, client_writer))
            else:
                client_writer.write(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                await client_writer.drain()
                client_writer.close()
                up_writer.close()
        else:
            # HTTP thông thường
            up_writer.write(req_line)
            up_writer.write(f"Proxy-Authorization: Basic {auth_token}\r\n".encode())
            for h in headers:
                if not h.lower().startswith(b"proxy-authorization:"):
                    up_writer.write(h)
            up_writer.write(b"\r\n")
            await up_writer.drain()
            
            asyncio.create_task(pipe(client_reader, up_writer))
            asyncio.create_task(pipe(up_reader, client_writer))
            
    except Exception as e:
        client_writer.close()

async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", LOCAL_PORT)
    print(f"[*] Proxy Bridge đang chạy tại 0.0.0.0:{LOCAL_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
