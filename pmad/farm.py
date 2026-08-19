import json
import os
import sys
import time
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
FARM_URL = "https://lexynova.com/pmads/api.php"
FARM_INTERVAL = 7200
REQUEST_TIMEOUT = 30

LOGIN_HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://lexynova.com",
    "Referer": "https://lexynova.com/pmads/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0"
    ),
}

FARM_HEADERS = {
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


def clear_line() -> None:
    print("\r" + (" " * 100) + "\r", end="")


def print_banner() -> None:
    print(Fore.CYAN + figlet_format("FARM BOT", font="slant"))
    print(Fore.WHITE + "LexyNova PMADS | Multi-account farm scheduler")
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


def login(session: requests.Session, init_data: str) -> str:
    response = session.post(
        LOGIN_URL,
        headers=LOGIN_HEADERS,
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
    return token


def farm_account(account_number: int, init_data: str) -> bool:
    session = requests.Session()
    try:
        print(Fore.YELLOW + f"[{account_number}] Login...", end=" ")
        token = login(session, init_data)
        print(Fore.GREEN + "BERHASIL")

        headers = {**FARM_HEADERS, "X-User-Token": token}

        # Step 1: Claim farm (klaim hasil farm sebelumnya)
        print(Fore.YELLOW + f"[{account_number}] Claim farm...", end=" ")
        try:
            response_claim = session.post(
                FARM_URL,
                headers=headers,
                json={"action": "farm_claim"},
                timeout=REQUEST_TIMEOUT,
            )
            response_claim.raise_for_status()
            payload_claim = parse_response(response_claim)
            print(
                Fore.GREEN
                + "BERHASIL "
                + Fore.WHITE
                + f"(HTTP {response_claim.status_code})"
            )
            print(Fore.LIGHTBLACK_EX + f"    Respons: {short_response(payload_claim)}")
        except requests.RequestException as exc:
            print(Fore.YELLOW + f"SKIP ({type(exc).__name__}: {exc})")
        except Exception as exc:
            print(Fore.YELLOW + f"SKIP ({exc})")

        time.sleep(1)

        # Step 2: Start farm baru
        print(Fore.YELLOW + f"[{account_number}] Start farm...", end=" ")
        response = session.post(
            FARM_URL,
            headers=headers,
            json={"action": "farm_start"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = parse_response(response)
        print(
            Fore.GREEN
            + "BERHASIL "
            + Fore.WHITE
            + f"(HTTP {response.status_code})"
        )
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
            + f"Next farm dalam {hours:02d}:{minutes:02d}:{secs:02d}"
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
            print(Fore.MAGENTA + Style.BRIGHT + f"=== SIKLUS {cycle} ===")
            success_count = 0
            for account_number, init_data in enumerate(accounts, start=1):
                if farm_account(account_number, init_data):
                    success_count += 1
                time.sleep(0.5)

            print(
                Fore.WHITE
                + f"\nSelesai: {success_count}/{len(accounts)} akun berhasil."
            )
            print(Fore.LIGHTBLACK_EX + "Menunggu 2 jam sebelum siklus berikutnya...\n")
            countdown(FARM_INTERVAL)
            cycle += 1

    except KeyboardInterrupt:
        clear_line()
        print(Fore.YELLOW + "\nBot dihentikan oleh pengguna.")


if __name__ == "__main__":
    run()
