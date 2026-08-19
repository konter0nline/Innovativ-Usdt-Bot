
import os
import sys
import time
import random
from datetime import datetime
import requests
import pyfiglet
from colorama import init, Fore, Style

# Inisialisasi colorama
init(autoreset=True)

# Konstanta warna
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RED = Fore.RED
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
WHITE = Fore.WHITE


def LG(message):
    print(f"{GREEN}{BOLD}[INFO] {message}{RESET}")


def LE(message):
    print(f"{RED}{BOLD}[ERROR] {message}{RESET}")


# ==================== KONFIGURASI ====================
BASE_URL = "https://lexynova.com/pmads"

# Task ID Twitter + Mission yang bisa di-claim tanpa verifikasi
TWITTER_TASK_IDS = [
    "m_2d4dc6d6",
    "m_33f251af",
    "m_687ca3ab",
    "m_dc173581",
    "m_d9083736",
    "m_ee607bbd",
    "m_ba8278d9",
    "m_b2435fe9",
]

# Task ID Telegram (join channel) - bypass dengan delay 5 detik sebelum claim
TELEGRAM_TASK_IDS = [
    "m_08bc08f5",
    "m_27c831ed",
    "m_474d24ef",
    "m_55fe2236",
    "m_70fb9b77",
    "m_935bb2a2",
    "m_9623f59d",
    "m_99498231",
    "m_a6178fb3",
    "m_a62d7550",
    "m_a8fdb21d",
    "m_ae3bb758",
    "m_b9006445",
]


class TaskBot:
    def __init__(self, init_data, account_id):
        self.init_data = init_data.strip()
        self.account_id = account_id
        self.token = None
        self.user_info = None
        self.session = requests.Session()

    def _log(self, message, level="info"):
        prefix = f"[Akun #{self.account_id}] "
        if level == "info":
            print(f"{GREEN}{BOLD}{prefix}{message}{RESET}")
        elif level == "warning":
            print(f"{YELLOW}{BOLD}{prefix}{message}{RESET}")
        elif level == "error":
            print(f"{RED}{BOLD}{prefix}{message}{RESET}")
        elif level == "success":
            print(f"{CYAN}{BOLD}{prefix}{message}{RESET}")

    def _base_headers(self):
        headers = {
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
            "Priority": "u=1, i",
        }
        if self.token:
            headers["X-User-Token"] = self.token
        return headers

    def login(self):
        """Login via POST /pmads/initdata.php"""
        self._log("Melakukan login...")
        try:
            url = f"{BASE_URL}/initdata.php"
            payload = {"init_data": self.init_data}
            response = self.session.post(url, headers=self._base_headers(), json=payload)

            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    self.token = data.get("token", "")
                    self.user_info = data.get("user", {})
                    username = self.user_info.get("username", "Unknown")
                    self._log(f"Login berhasil! Selamat datang, {username}", level="success")
                    self._log(f"Token: {self.token[:20]}...")
                    return True
                else:
                    self._log(f"Login gagal: {data.get('message', 'Unknown error')}", level="error")
                    return False
            else:
                self._log(f"Login gagal. Status: {response.status_code}", level="error")
                return False
        except Exception as e:
            self._log(f"Error saat login: {e}", level="error")
            return False

    def complete_twitter_tasks(self):
        """Claim semua task Twitter + Mission"""
        self._log(f"Memulai claim {len(TWITTER_TASK_IDS)} task Twitter/Mission...")
        completed = 0

        for mission_id in TWITTER_TASK_IDS:
            self._log(f"  Claiming task: {mission_id}...")
            try:
                api_url = f"{BASE_URL}/api.php"
                payload = {"action": "complete_mission", "missionId": mission_id}
                response = self.session.post(api_url, headers=self._base_headers(), json=payload)

                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("ok") or data.get("success"):
                            reward = data.get("reward", 10)
                            self._log(f"  Task {mission_id} berhasil! +{reward}", level="success")
                            completed += 1
                        else:
                            msg = data.get("message", data.get("error", "Unknown"))
                            self._log(f"  Task {mission_id} gagal: {msg}", level="warning")
                    except:
                        self._log(f"  Response: {response.text[:100]}", level="warning")
                else:
                    self._log(f"  Gagal. Status: {response.status_code}", level="error")
            except Exception as e:
                self._log(f"  Error: {e}", level="error")

            time.sleep(random.uniform(1.5, 2.5))

        self._log(f"Selesai! {completed}/{len(TWITTER_TASK_IDS)} task Twitter/Mission berhasil.", level="success")

    def complete_telegram_tasks(self):
        """Claim semua task Telegram (join channel) - bypass dengan delay 5 detik"""
        self._log(f"Memulai claim {len(TELEGRAM_TASK_IDS)} task Telegram (join channel)...")
        completed = 0

        for mission_id in TELEGRAM_TASK_IDS:
            self._log(f"  Klik join channel: {mission_id}...")
            # Tunggu 5 detik sebelum claim (bypass join channel)
            time.sleep(5)
            self._log(f"  Claiming task: {mission_id}...")
            try:
                api_url = f"{BASE_URL}/api.php"
                payload = {"action": "complete_mission", "missionId": mission_id}
                response = self.session.post(api_url, headers=self._base_headers(), json=payload)

                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("ok") or data.get("success"):
                            reward = data.get("reward", 10)
                            self._log(f"  Task {mission_id} berhasil! +{reward}", level="success")
                            completed += 1
                        else:
                            msg = data.get("message", data.get("error", "Unknown"))
                            self._log(f"  Task {mission_id} gagal: {msg}", level="warning")
                    except:
                        self._log(f"  Response: {response.text[:100]}", level="warning")
                else:
                    self._log(f"  Gagal. Status: {response.status_code}", level="error")
            except Exception as e:
                self._log(f"  Error: {e}", level="error")

            time.sleep(random.uniform(0.5, 1))

        self._log(f"Selesai! {completed}/{len(TELEGRAM_TASK_IDS)} task Telegram berhasil.", level="success")

    def run(self):
        """Jalankan bot untuk satu akun"""
        print(f"\n{CYAN}{'=' * 55}{RESET}")
        self._log("Memulai bot...")

        # Step 1: Login
        if not self.login():
            self._log("Login gagal. Berhenti.", level="error")
            return

        time.sleep(random.uniform(1, 1.5))

        # Step 2: Claim task Twitter + Mission
        self._log("\n--- AUTO CLAIM TWITTER/MISSION TASKS ---")
        self.complete_twitter_tasks()
        time.sleep(random.uniform(1, 2))

        # Step 3: Claim task Telegram (join channel bypass)
        self._log("\n--- AUTO CLAIM TELEGRAM TASKS (JOIN CHANNEL) ---")
        self.complete_telegram_tasks()

        self._log("\nSemua task selesai untuk akun ini!", level="success")
        print(f"{CYAN}{'=' * 55}{RESET}\n")


def banner():
    os.system("cls" if os.name == "nt" else "clear")
    ascii_art = pyfiglet.figlet_format("TASK BOT", font="slant")
    print(CYAN + BOLD + ascii_art + RESET)
    print(MAGENTA + BOLD + "Innovative USDT - Task Claimer" + RESET)
    print(YELLOW + "Auto Twitter Tasks | Auto Telegram Join Channel" + RESET)
    print(CYAN + "=" * 55 + RESET)
    time_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(f"{WHITE}Waktu: {time_str}{RESET}\n")


def load_data(path):
    """Baca init_data dari file data.txt"""
    if not os.path.exists(path):
        LE(f"File {path} tidak ditemukan!")
        print(f"{YELLOW}Buat file data.txt dan isi dengan init_data (satu per baris).{RESET}")
        return []
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]


def main():
    banner()

    data_file = "data.txt"
    accounts = load_data(data_file)

    if not accounts:
        return

    LG(f"Ditemukan {len(accounts)} akun.\n")

    for i, init_data in enumerate(accounts, 1):
        bot = TaskBot(init_data, i)
        bot.run()

        # Delay antar akun
        if i < len(accounts):
            delay = random.uniform(2, 3)
            LG(f"Menunggu {delay:.1f} detik sebelum akun berikutnya...")
            time.sleep(delay)

    LG("Semua akun telah diproses!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}{BOLD}Bot dihentikan oleh pengguna.{RESET}")
        sys.exit()
