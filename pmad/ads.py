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
ADSGRAM_API = "https://api.adsgram.ai"
BOT_USERNAME = "Innovativeusdtbot"
BLOCK_ID = "38775"


class AdsBot:
    def __init__(self, init_data, account_id):
        self.init_data = init_data.strip()
        self.account_id = account_id
        self.token = None
        self.user_info = None
        self.settings = None
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

    def _adsgram_headers(self):
        """Headers untuk request ke api.adsgram.ai"""
        headers = {
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
            "X-Color-Scheme": "dark",
            "X-Is-Fullscreen": "false",
            "X-Viewport-Height": "590",
        }
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

    def get_user_data(self):
        """Ambil data user via GET /pmads/userdata.php"""
        self._log("Mengambil data user...")
        try:
            url = f"{BASE_URL}/userdata.php"
            response = self.session.get(url, headers=self._base_headers())

            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    self.user_info = data.get("user", {})
                    self.settings = data.get("settings", {})

                    username = self.user_info.get("username", "Unknown")
                    self._log(f"Username: {username}", level="success")

                    if self.settings:
                        ad_reward = self.settings.get("adReward", 0)
                        max_daily_ads = self.settings.get("maxDailyAds", 0)
                        self._log(f"Reward per iklan: {ad_reward}")
                        self._log(f"Max iklan harian: {max_daily_ads}")

                    return True
                else:
                    self._log("Gagal mengambil data user", level="error")
                    return False
            else:
                self._log(f"Gagal mengambil data user. Status: {response.status_code}", level="error")
                return False
        except Exception as e:
            self._log(f"Error saat mengambil data user: {e}", level="error")
            return False

    def _simulate_ad(self):
        """
        Simulasi nonton iklan adsgram.
        Return True jika berhasil simulasi, False jika gagal.
        """
        record = ""

        try:
            tg_id = self.user_info.get("telegramId", "") if self.user_info else ""

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

            adv_url = f"{ADSGRAM_API}/adv"
            response = self.session.get(adv_url, params=adv_params, headers=self._adsgram_headers())

            if response.status_code == 200:
                self._log("    Iklan berhasil di-request", level="success")
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

                    if record:
                        self._log(f"    Record: {record[:30]}...", level="info")

                except Exception as parse_err:
                    self._log(f"    Gagal parse response: {parse_err}", level="warning")
            else:
                self._log(f"    Gagal request iklan. Status: {response.status_code}", level="warning")

            time.sleep(random.uniform(0.3, 0.5))

            # Render event
            if record:
                event_url = f"{ADSGRAM_API}/event"
                event_params = {"record": record, "type": "Render", "trackingtypeid": "13"}
                try:
                    self.session.get(event_url, params=event_params, headers=self._adsgram_headers())
                except:
                    pass

                time.sleep(random.uniform(0.2, 0.3))

                # Show event
                event_params = {"record": record, "type": "Show", "trackingtypeid": "0"}
                try:
                    self.session.get(event_url, params=event_params, headers=self._adsgram_headers())
                except:
                    pass

            # Tunggu simulasi nonton iklan (batas aman minimum)
            watch_time = random.uniform(3, 5)
            self._log(f"    Menunggu {watch_time:.1f}s (simulasi nonton)...")
            time.sleep(watch_time)

            # Reward event
            if record:
                event_url = f"{ADSGRAM_API}/event"
                event_params = {"record": record, "type": "Reward", "trackingtypeid": "2"}
                try:
                    self.session.get(event_url, params=event_params, headers=self._adsgram_headers())
                except:
                    pass

                time.sleep(random.uniform(0.2, 0.3))

            return True

        except Exception as e:
            self._log(f"    Error simulasi iklan: {e}", level="warning")
            return False

    def watch_ad(self):
        """
        Nonton iklan dan claim reward.
        Flow: simulasi adsgram → POST api.php {action: "watch_ad"}
        """
        self._log("Memulai nonton iklan...")

        # Simulasi adsgram
        self._simulate_ad()

        # Claim reward
        self._log("  Mengklaim reward iklan...")
        try:
            api_url = f"{BASE_URL}/api.php"
            payload = {"action": "watch_ad"}
            response = self.session.post(api_url, headers=self._base_headers(), json=payload)

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("ok") or data.get("success"):
                        reward = data.get("reward", self.settings.get("adReward", 15) if self.settings else 15)
                        self._log(f"  Reward iklan berhasil! +{reward}", level="success")
                        return True
                    else:
                        msg = data.get("message", data.get("error", "Unknown"))
                        self._log(f"  Gagal klaim: {msg}", level="warning")
                        return False
                except:
                    self._log(f"  Response: {response.text[:200]}", level="warning")
                    return False
            else:
                self._log(f"  Gagal. Status: {response.status_code}", level="error")
                return False
        except Exception as e:
            self._log(f"  Error: {e}", level="error")
            return False

    def auto_watch_ads(self):
        """Otomatis nonton iklan sampai batas harian"""
        max_ads = 14
        if self.settings:
            max_ads = self.settings.get("maxDailyAds", 14)

        self._log(f"Memulai auto watch ads (max {max_ads} iklan per hari)...")
        success_count = 0

        for i in range(max_ads):
            self._log(f"\n--- Iklan #{i+1}/{max_ads} ---")
            if self.watch_ad():
                success_count += 1
            else:
                self._log("Gagal atau sudah mencapai batas. Berhenti.", level="warning")
                break

            # Delay antar iklan (batas aman)
            if i < max_ads - 1:
                delay = random.uniform(1, 2)
                self._log(f"Menunggu {delay:.1f}s sebelum iklan berikutnya...")
                time.sleep(delay)

        self._log(f"Selesai! {success_count} iklan berhasil ditonton.", level="success")

    def run(self):
        """Jalankan bot untuk satu akun"""
        print(f"\n{CYAN}{'=' * 55}{RESET}")
        self._log("Memulai bot...")

        # Step 1: Login
        if not self.login():
            self._log("Login gagal. Berhenti.", level="error")
            return

        time.sleep(random.uniform(1, 1.5))

        # Step 2: Get user data (untuk dapat max daily ads)
        self.get_user_data()
        time.sleep(random.uniform(0.5, 1))

        # Step 3: Auto watch ads
        self._log("\n--- AUTO WATCH ADS ---")
        self.auto_watch_ads()

        self._log("\nSemua iklan selesai untuk akun ini!", level="success")
        print(f"{CYAN}{'=' * 55}{RESET}\n")


def banner():
    os.system("cls" if os.name == "nt" else "clear")
    ascii_art = pyfiglet.figlet_format("ADS BOT", font="slant")
    print(CYAN + BOLD + ascii_art + RESET)
    print(MAGENTA + BOLD + "Innovative USDT - Auto Watch Ads" + RESET)
    print(YELLOW + "Simulasi Adsgram | Auto Claim Reward" + RESET)
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
        bot = AdsBot(init_data, i)
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
