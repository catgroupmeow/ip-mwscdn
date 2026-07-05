"""
Сканер IP для MWS CDN (catgroupmeow.xyz) - исправленная версия
Использует сокеты + TLS, двойная проверка найденных IP.
Успех = HTTP 400.
"""

import ipaddress
import socket
import ssl
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

DOMAIN = "catgroupmeow.xyz"
API_PATH = "/api/v4/assets/"
PORT = 443
EXPECTED_CODES = [400]
DEFAULT_WORKERS = 20
DEFAULT_TIMEOUT = 5
RETRY_TIMEOUT = 10  # таймаут для повторной проверки

SUBNETS = [
    "89.249.52.0/22",
    "188.72.77.0/24",
    "37.18.27.0/24",
    "94.139.242.0/24",
    "176.122.21.0/24",
    "80.251.156.0/24",
    "185.233.3.0/24",
    "176.122.23.0/24",
    "178.170.219.0/24",
    "37.18.32.0/23",
    "94.139.240.0/24",
    "176.122.27.0/24",
    "176.122.20.0/24",
    "89.169.90.0/24",
]

def generate_ips():
    all_ips = []
    for cidr in SUBNETS:
        try:
            net = ipaddress.ip_network(cidr, strict=False)
            ips = [str(ip) for ip in net.hosts()]
            all_ips.extend(ips)
            print(f"    {cidr} -> {len(ips)} адресов")
        except Exception as e:
            print(f"    ⚠️ Ошибка в подсети {cidr}: {e}")
    return all_ips

def check_ip_socket(ip, timeout):
    """Проверяет IP через сокет + TLS, возвращает (ip, is_ok, status_code)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, PORT))

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        if hasattr(ssl, 'OP_ENABLE_RENEGOTIATION'):
            context.options |= ssl.OP_ENABLE_RENEGOTIATION

        tls_sock = context.wrap_socket(sock, server_hostname=DOMAIN)

        request = (
            f"GET {API_PATH} HTTP/1.1\r\n"
            f"Host: {DOMAIN}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        tls_sock.send(request.encode())

        response = b""
        while True:
            chunk = tls_sock.recv(4096)
            if not chunk:
                break
            response += chunk
            if b"\r\n\r\n" in response:
                break

        tls_sock.close()

        if response:
            status_line = response.split(b"\r\n")[0].decode("utf-8", errors="ignore")
            if status_line.startswith("HTTP/") and " " in status_line:
                code = int(status_line.split(" ")[1])
                return ip, code in EXPECTED_CODES, code

        return ip, False, None

    except Exception:
        return ip, False, None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("-t", "--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    print("[*] Генерируем список IP-адресов из подсетей...")
    all_ips = generate_ips()
    total = len(all_ips)
    print(f"\n[*] Всего IP: {total}")
    print(f"[*] Первичная проверка (таймаут {args.timeout} сек)...\n")

    # Первый проход
    found = []
    completed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(check_ip_socket, ip, args.timeout): ip for ip in all_ips}
        for future in as_completed(futures):
            completed += 1
            ip, is_ok, code = future.result()
            if is_ok:
                found.append(ip)
                status = "✅"
            else:
                status = "❌"
            code_str = f" (HTTP {code})" if code is not None else " (ошибка)"
            print(f"[{completed}/{total}] {ip} {status}{code_str}")

    print(f"\n[*] Найдено {len(found)} IP, предположительно рабочих.")
    if not found:
        print("❌ Не найдено ни одного IP. Завершаем.")
        return

    # Повторная проверка найденных IP с увеличенным таймаутом
    print(f"[*] Повторная проверка {len(found)} IP (таймаут {RETRY_TIMEOUT} сек)...\n")
    confirmed = []
    completed = 0
    with ThreadPoolExecutor(max_workers=min(args.workers, len(found))) as executor:
        futures = {executor.submit(check_ip_socket, ip, RETRY_TIMEOUT): ip for ip in found}
        for future in as_completed(futures):
            completed += 1
            ip, is_ok, code = future.result()
            if is_ok:
                confirmed.append(ip)
                status = "✅"
            else:
                status = "❌"
            code_str = f" (HTTP {code})" if code is not None else " (ошибка)"
            print(f"[{completed}/{len(found)}] {ip} {status}{code_str}")

    print("\n" + "=" * 60)
    if confirmed:
        unique = sorted(set(confirmed))
        print(f"✅ Окончательно подтверждено {len(unique)} IP, отвечающих {EXPECTED_CODES}:")
        for ip in unique:
            print(f"  - {ip}")

        with open("ip_final.txt", "w") as f:
            f.write("\n".join(unique))
        print("\n💾 Финальный список сохранён в ip_final.txt")
    else:
        print("❌ После повторной проверки ни один IP не подтвердился.")

if __name__ == "__main__":
    main()
