import json
import os
import sys
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from colorama import Fore, Style, init as colorama_init
from pyfiglet import figlet_format

colorama_init(autoreset=True)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.txt"
LOGIN_URL = "https://lexynova.com/pmads/initdata.php"
API_URL = "https://lexynova.com/pmads/api.php"
ADSGRAM_API = "https://api.adsgram.ai"
BOT_USERNAME = "Innovativeusdtbot"
BLOCK_ID = "38775"
SPIN_INTERVAL = 10800  # 3 jam dalam detik
REQUEST_TIMEOUT = 30

BASE_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://lexynova.com",
    "Referer": "https://lexynova.com/pmads/",
    "Sec-Ch-Ua": '"Chromium";v="151", "Not-A?Brand";v="99", "Microsoft Edge WebView2";v="151", "Microsoft Edge";v="151"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0"
    ),
    "Priority": "u=1, i",
}

ADSGRAM_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "api.adsgram.ai",
    "Origin": "https://lexynova.com",
    "Referer": "https://lexynova.com/",
    "Sec-Ch-Ua": '"Chromium";v="151", "Not-A?Brand";v="99", "Microsoft Edge WebView2";v="151", "Microsoft Edge";v="151"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0"
    ),
    "X-Color-Scheme": "dark",
    "X-Is-Fullscreen": "false",
    "X-Viewport-Height": "590",
}


def clear_line() -> None:
    print("\r" + (" " * 100) + "\r", end="")


def print_banner() -> None:
    print(Fore.CYAN + figlet_format("SPIN BOT", font="slant"))
    print(Fore.WHITE + "LexyNova PMADS | Multi-account spin scheduler (setiap 3 jam)")
    print(Fore.LIGHTBLACK_EX + f"Data file: {DATA_FILE}\n")


def load_init_data() -> list[str]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {DATA_FILE}")

    accounts = []
    for line in DATA_FILE.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value and not value.startswith("#"):
            accounts.append(value)

    if not accounts:
        raise ValueError("data.txt kosong. Isi satu init_data per baris.")
    return accounts


def parse_response(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text.strip()


def find_token(payload: Any) -> str | None:
    """Find a token across common JSON response shapes."""
    if isinstance(payload, dict):
        for key in ("token", "user_token", "access_token", "x_user_token"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        for key in ("data", "user", "result", "account"):
            nested = payload.get(key)
            token = find_token(nested)
            if token:
                return token

    elif isinstance(payload, list):
        for item in payload:
            token = find_token(item)
            if token:
                return token

    return None


def short_response(payload: Any, limit: int = 240) -> str:
    if isinstance(payload, (dict, list)):
        text = json.dumps(payload, ensure_ascii=False)
    else:
        text = str(payload)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def login(session: requests.Session, init_data: str) -> tuple[str, str]:
    """Login dan return (token, telegram_id)."""
    response = session.post(
        LOGIN_URL,
        headers={**BASE_HEADERS},
        json={"init_data": init_data},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = parse_response(response)
    token = find_token(payload)
    if not token:
        raise RuntimeError(
            "Token tidak ditemukan pada respons login: " + short_response(payload)
        )

    # Coba ambil telegram ID
    tg_id = ""
    if isinstance(payload, dict):
        user = payload.get("user", {})
        if isinstance(user, dict):
            tg_id = str(user.get("telegramId", user.get("telegram_id", "")))

    return token, tg_id


def simulate_ad(session: requests.Session, tg_id: str) -> bool:
    """Simulasi nonton iklan adsgram. Return True jika berhasil."""
    record = ""

    try:
        adv_params = {
            "blockId": BLOCK_ID,
            "tg_id": str(tg_id),
            "tg_platform": "tdesktop",
            "platform": "Win32",
            "language": "id",
            "top_domain": "lexynova.com",
            "connectionType": "wifi",
            "sdk_version": "2.2.1",
        }

        response = session.get(
            f"{ADSGRAM_API}/adv",
            params=adv_params,
            headers=ADSGRAM_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            try:
                ad_data = response.json()
                trackings = ad_data.get("banner", {}).get("trackings", [])
                if trackings:
                    for tracking in trackings:
                        if tracking.get("name") == "render" or tracking.get("type") == "Render":
                            record = tracking.get("value", "")
                            break
                    if not record and trackings:
                        record = trackings[0].get("value", "")

                if not record:
                    record = ad_data.get("record", "")

                if not record:
                    banner_id = ad_data.get("banner", {}).get("id", "")
                    if banner_id:
                        record = str(banner_id)
            except Exception:
                pass

        time.sleep(random.uniform(1, 2))

        # Render event
        if record:
            event_url = f"{ADSGRAM_API}/event"
            try:
                session.get(event_url, params={"record": record, "type": "Render", "trackingtypeid": "13"}, headers=ADSGRAM_HEADERS, timeout=10)
            except Exception:
                pass

            time.sleep(random.uniform(0.5, 1))

            # Show event
            try:
                session.get(event_url, params={"record": record, "type": "Show", "trackingtypeid": "0"}, headers=ADSGRAM_HEADERS, timeout=10)
            except Exception:
                pass

        # Simulasi nonton iklan
        watch_time = random.uniform(5, 8)
        time.sleep(watch_time)

        # Reward event
        if record:
            event_url = f"{ADSGRAM_API}/event"
            try:
                session.get(event_url, params={"record": record, "type": "Reward", "trackingtypeid": "2"}, headers=ADSGRAM_HEADERS, timeout=10)
            except Exception:
                pass

            time.sleep(random.uniform(0.5, 1))

        return True

    except Exception:
        return False


def spin_account(account_number: int, init_data: str) -> bool:
    """Login, simulasi ad, spin, claim spin untuk satu akun."""
    session = requests.Session()
    try:
        # Step 1: Login
        print(Fore.YELLOW + f"[{account_number}] Login...", end=" ")
        token, tg_id = login(session, init_data)
        print(Fore.GREEN + "BERHASIL")

        headers = {**BASE_HEADERS, "X-User-Token": token}

        # Step 2: Simulasi nonton iklan (wajib sebelum spin)
        print(Fore.YELLOW + f"[{account_number}] Nonton iklan...", end=" ")
        ad_success = simulate_ad(session, tg_id)
        if ad_success:
            print(Fore.GREEN + "SELESAI")
        else:
            print(Fore.YELLOW + "SKIP (lanjut spin)")

        # Step 3: Spin
        print(Fore.YELLOW + f"[{account_number}] Spin...", end=" ")
        response = session.post(
            API_URL,
            headers=headers,
            json={"action": "spin"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = parse_response(response)

        if isinstance(payload, dict):
            if payload.get("ok") or payload.get("success"):
                result = payload.get("result", payload.get("reward", "?"))
                print(Fore.GREEN + f"BERHASIL (Hasil: {result})")
            else:
                msg = payload.get("message", payload.get("error", "Unknown"))
                print(Fore.RED + f"GAGAL ({msg})")
                return False
        else:
            print(Fore.GREEN + f"OK (HTTP {response.status_code})")
            print(Fore.LIGHTBLACK_EX + f"    Respons: {short_response(payload)}")

        time.sleep(random.uniform(3, 5))

        # Step 4: Claim spin
        print(Fore.YELLOW + f"[{account_number}] Claim spin...", end=" ")
        response = session.post(
            API_URL,
            headers=headers,
            json={"action": "claim_spin"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = parse_response(response)

        if isinstance(payload, dict):
            if payload.get("ok") or payload.get("success"):
                reward = payload.get("reward", payload.get("amount", "?"))
                print(Fore.GREEN + f"BERHASIL (+{reward})")
            else:
                msg = payload.get("message", payload.get("error", "Unknown"))
                print(Fore.YELLOW + f"SKIP ({msg})")
        else:
            print(Fore.GREEN + f"OK (HTTP {response.status_code})")

        print(Fore.LIGHTBLACK_EX + f"    Respons: {short_response(payload)}")
        return True

    except requests.RequestException as exc:
        print(Fore.RED + f"GAGAL ({type(exc).__name__}: {exc})")
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(Fore.RED + f"GAGAL ({exc})")
    finally:
        session.close()
    return False


def countdown(seconds: int) -> None:
    end_time = time.monotonic() + seconds
    while True:
        remaining = max(0, int(end_time - time.monotonic()))
        hours, remainder = divmod(remaining, 3600)
        minutes, secs = divmod(remainder, 60)
        now = datetime.now().strftime("%H:%M:%S")
        clear_line()
        print(
            Fore.CYAN
            + f"Next spin dalam {hours:02d}:{minutes:02d}:{secs:02d}"
            + Fore.LIGHTBLACK_EX
            + f" | sekarang {now} | Ctrl+C untuk berhenti",
            end="",
            flush=True,
        )
        if remaining <= 0:
            clear_line()
            print(Fore.GREEN + "Waktu tunggu selesai. Memulai siklus berikutnya...\n")
            return
        time.sleep(1)


def run() -> None:
    print_banner()
    try:
        accounts = load_init_data()
    except (FileNotFoundError, ValueError) as exc:
        print(Fore.RED + f"Error: {exc}")
        sys.exit(1)

    print(Fore.WHITE + f"Memuat {len(accounts)} akun dari data.txt.\n")
    cycle = 1

    try:
        while True:
            print(Fore.MAGENTA + Style.BRIGHT + f"=== SIKLUS SPIN {cycle} ===")
            success_count = 0
            for account_number, init_data in enumerate(accounts, start=1):
                if spin_account(account_number, init_data):
                    success_count += 1
                # Delay antar akun
                if account_number < len(accounts):
                    time.sleep(random.uniform(3, 5))

            print(
                Fore.WHITE
                + f"\nSelesai: {success_count}/{len(accounts)} akun berhasil spin."
            )
            print(Fore.LIGHTBLACK_EX + "Menunggu 3 jam sebelum siklus berikutnya...\n")
            countdown(SPIN_INTERVAL)
            cycle += 1

    except KeyboardInterrupt:
        clear_line()
        print(Fore.YELLOW + "\nBot dihentikan oleh pengguna.")


if __name__ == "__main__":
    run()
