#!/usr/bin/env python3
"""
Сканер IP для MWS CDN (catgroupmeow.xyz)
Путь: /api/v4/assets/
Успех = HTTP 400
Использует curl для проверки (через --resolve)
"""

import subprocess
import concurrent.futures
import time
import ipaddress
import sys
import platform
import argparse

# ---------- Конфигурация ----------
DOMAIN = "catgroupmeow.xyz"
API_PATH = "/api/v4/assets/"
PORT = "443"
CONNECT_TIMEOUT = "5"
DEFAULT_WORKERS = 20
DEFAULT_TIMEOUT = 8
EXPECTED_CODES = [400]
# ---------------------------------

IS_WINDOWS = platform.system() == "Windows"
NULL_DEVICE = "NUL" if IS_WINDOWS else "/dev/null"

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

def check_curl():
    try:
        subprocess.run(["curl", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

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

def check_ip(ip, timeout):
    cmd = [
        "curl",
        "-s",
        "-o", NULL_DEVICE,
        "-w", "%{http_code}",
        "--resolve", f"{DOMAIN}:{PORT}:{ip}",
        "--connect-timeout", CONNECT_TIMEOUT,
        "--max-time", str(timeout),
        "-k",
        "-L",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        f"https://{DOMAIN}:{PORT}{API_PATH}"
    ]

    if IS_WINDOWS:
        try:
            idx = cmd.index("-k")
            cmd.insert(idx + 1, "--ssl-no-revoke")
        except ValueError:
            pass

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 2,
            encoding='utf-8',
            errors='ignore'
        )
        status = result.stdout.strip()
        if status.isdigit():
            code = int(status)
            return ip, code in EXPECTED_CODES, code
        return ip, False, None
    except subprocess.TimeoutExpired:
        return ip, False, None
    except Exception:
        return ip, False, None

def main():
    parser = argparse.ArgumentParser(description="Сканер IP для MWS CDN (catgroupmeow.xyz)")
    parser.add_argument("-w", "--workers", type=int, default=DEFAULT_WORKERS,
                        help=f"Количество потоков (по умолчанию {DEFAULT_WORKERS})")
    parser.add_argument("-t", "--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Таймаут на запрос в секундах (по умолчанию {DEFAULT_TIMEOUT})")
    args = parser.parse_args()

    print("[*] Проверка наличия curl...")
    if not check_curl():
        print("[!] curl не найден! Установите: pkg install curl (или скачайте с curl.se)")
        sys.exit(1)

    print("[*] Генерируем список IP-адресов...")
    all_ips = generate_ips()
    total = len(all_ips)
    print(f"\n[*] Всего IP: {total}")
    print(f"[*] Ищем IP с ответом {EXPECTED_CODES} на {API_PATH}...\n")

    found = []
    completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(check_ip, ip, args.timeout): ip for ip in all_ips}

        for future in concurrent.futures.as_completed(futures):
            completed += 1
            ip, is_ok, code = future.result()
            if is_ok:
                found.append(ip)
                status = "✅"
            else:
                status = "❌"
            code_str = f" (HTTP {code})" if code is not None else " (ошибка)"
            print(f"[{completed}/{total}] {ip} {status}{code_str}")

    print("\n" + "=" * 60)
    if found:
        unique = sorted(set(found))
        print(f"✅ Найдено {len(unique)} IP, отвечающих {EXPECTED_CODES}:")
        for ip in unique:
            print(f"  - {ip}")

        with open("ip.txt", "w") as f:
            f.write("\n".join(unique))
        print("\n💾 Список сохранён в ip.txt")
    else:
        print("❌ Не найдено ни одного подходящего IP.")

if __name__ == "__main__":
    main()
