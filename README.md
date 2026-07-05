# 🌐 IP-адреса MWS Cloud CDN

<div align="center">
  
**Актуальные рабочие IP-адреса CDN-сети MWS Cloud (МТС)**  
*Автоматический сканер подсетей + готовые к использованию адреса*

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20|%20linux%20|%20macos-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

</div>

---

## ✅ Текущие рабочие IP

Проверены **04.07.2026** — все адреса отвечают на HTTPS:

```bash
89.169.90.8   
89.169.90.9   
89.169.90.10  
89.169.90.11  
```

> 💡 **Подсеть:** `89.169.90.0/24` — все адреса из этого диапазона потенциально рабочие

---

## 🚀 Быстрый старт

### Автоматическое сканирование
```bash

git clone https://github.com/catgroupmeow/ip-mwscdn.git
cd ip-mwscdn
python scanner.py

# Результат в ip.txt
```

---

## 🔧 Установка сканера

### 📋 Требования
- **Python 3.6+**
- **curl**

### 🖥️ По платформам

<details>
<summary><b>🐧 Ubuntu/Debian</b></summary>

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv curl git -y
```
</details>

<details>
<summary><b>🍎 macOS</b></summary>

```bash
brew install python curl git
```
</details>

<details>
<summary><b>🪟 Windows</b></summary>

1. Скачайте [Python](https://python.org/downloads/) (✅ Add Python to PATH)
2. Скачайте [curl](https://curl.se/windows/) или используйте встроенный
3. Установите [Git](https://git-scm.com/download/win)
</details>

<details>
<summary><b>📱 Termux (Android)</b></summary>

```bash
pkg update && pkg install python curl git -y
# Виртуальное окружение не требуется
```
</details>

---

## ⚡ Пошаговый запуск

### 1️⃣ Клонирование
```bash
git clone https://github.com/catgroupmeow/ip-mwscdn.git
cd ip-mwscdn
```

### 2️⃣ Виртуальное окружение *(опционально)*

<details>
<summary><b>Linux/macOS</b></summary>

```bash
python3 -m venv venv
source venv/bin/activate
```
</details>

<details>
<summary><b>Windows CMD</b></summary>

```cmd
python -m venv venv
venv\Scripts\activate
```
</details>

<details>
<summary><b>Windows PowerShell</b></summary>

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
</details>

### 3️⃣ Запуск сканера
```bash
python scanner.py
```

**Результат:** Рабочие IP сохранятся в `ip.txt`

### 4️⃣ Выход из окружения
```bash
deactivate  # Только если создавали venv
```

---

## 📊 Технические детали

### 🎯 Принцип работы
- Сканирует **14 подсетей** MWS Cloud
- Проверяет каждый IP через **curl + DNS resolve**
- Фильтрует по коду ответа **400 Bad Request**
- Многопоточность: **80 воркеров**

### 🌐 Полный список подсетей
```
89.249.52.0/22    188.72.77.0/24     37.18.27.0/24
94.139.242.0/24   176.122.21.0/24    80.251.156.0/24
185.233.3.0/24    176.122.23.0/24    178.170.219.0/24
37.18.32.0/23     94.139.240.0/24    176.122.27.0/24
176.122.20.0/24   89.169.90.0/24
```

---

## ⚖️ Отказ от ответственности

Данный репозиторий и содержащаяся в нём информация предоставляются **«как есть»** (as-is) без каких-либо гарантий, явных или подразумеваемых.

Автор не гарантирует:
- актуальность, точность или полноту предоставленных IP-адресов;
- постоянную доступность или работоспособность указанных узлов;
- отсутствие ошибок, перебоев или изменений в работе CDN-сети MWS Cloud.

Все IP-адреса получены путём автоматического сканирования открытых подсетей. Использование этих данных осуществляется **на ваш собственный риск и ответственность**.

Рекомендуется **самостоятельно проверять** IP-адреса перед их использованием в производственной среде и регулярно обновлять список с помощью скрипта `scanner.py`.

Автор не несёт ответственности за любые прямые или косвенные убытки, возникшие в результате использования информации из этого репозитория.

---

