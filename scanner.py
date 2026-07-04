import subprocess
import concurrent.futures
import time
import ipaddress

DOMAIN = "catgroupmeow.xyz"
API_PATH = "/api/v4/assets/"
PORT = "443"
TIMEOUT = "3"
MAX_WORKERS = 80

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
            all_ips.extend([str(ip) for ip in net.hosts()])
        except Exception as e:
            print(f"⚠️ Ошибка в подсети {cidr}: {e}")
    return all_ips

def check_ip(ip):
    cmd = [
        "curl", "-s", "-o", "NUL", "-w", "%{http_code}",
        "--resolve", f"{DOMAIN}:{PORT}:{ip}",
        "--connect-timeout", TIMEOUT,
        f"https://{DOMAIN}:{PORT}{API_PATH}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
        status = result.stdout.strip()
        if status == "400":
            return ip
    except:
        pass
    return None

def main():
    print("🔍 Генерируем список всех IP-адресов из подсетей...")
    all_ips = generate_ips()
    total = len(all_ips)
    print(f"✅ Всего IP для проверки: {total}")
    print(f"🔍 Проверяем через curl (параллельно {MAX_WORKERS} потоков)...")
    print("⏳ Ожидаемое время: ~2–4 минуты\n")

    found = []
    start_time = time.time()
    completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_ip = {executor.submit(check_ip, ip): ip for ip in all_ips}
        for future in concurrent.futures.as_completed(future_to_ip):
            completed += 1
            ip = future.result()
            if ip:
                found.append(ip)
                print(f"✅ [{completed}/{total}] {ip}")

            if completed % 100 == 0:
                elapsed = time.time() - start_time
                speed = completed / elapsed if elapsed > 0 else 0
                print(f"⏳ [{completed}/{total}] проверено. Скорость: {speed:.1f} IP/сек")

    elapsed_total = time.time() - start_time
    avg_speed = total / elapsed_total if elapsed_total > 0 else 0
    print("\n" + "="*60)
    print(f"✅ Завершено за {elapsed_total:.1f} сек, средняя скорость: {avg_speed:.1f} IP/сек")
    print(f"Найдено IP: {len(found)}")

    if found:
        unique_found = sorted(set(found))
        print(f"Уникальных IP: {len(unique_found)}")
        with open("ip.txt", "w") as f:
            f.write("\n".join(unique_found))
        print("💾 Список сохранён в ip.txt")
        print("\nНайденные работающие IP:")
        for ip in unique_found:
            print(f"  • {ip}")
    else:
        print("❌ Ничего не найдено.")

if __name__ == "__main__":
    main()
