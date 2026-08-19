import os
import sys
import json
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


def LW(message):
    print(f"{YELLOW}{BOLD}[WARN] {message}{RESET}")


def LE(message):
    print(f"{RED}{BOLD}[ERROR] {message}{RESET}")


def LS(message):
    print(f"{CYAN}{BOLD}[SUCCESS] {message}{RESET}")


# ==================== KONFIGURASI ====================
BASE_URL = "https://lexynova.com/pmads"
ADSGRAM_API = "https://api.adsgram.ai"
BOT_USERNAME = "Innovativeusdtbot"
BLOCK_ID = "38775"

# Task ID Twitter - claim langsung
TWITTER_TASK_IDS = [
    "m_2d4dc6d6",   # Follow Twitter And On Notification (reward: 12)
    "m_33f251af",   # Must Repost,Like, Comment, Bookmark (reward: 15)
    "m_687ca3ab",   # Must Like, Repost, And Positive Comment (reward: 10)
    "m_ba8278d9",   # Do Repost, Like, Positive Comment Must (reward: 10)
    "m_dc173581",   # Need Manager Repost This Post (reward: 10)
]

# Task ID Telegram (join channel) - bypass dengan delay 5 detik sebelum claim
TELEGRAM_TASK_IDS = [
    "m_08bc08f5",   # Casino Trading (reward: 10)
    "m_27c831ed",   # Join Trading X Crypto (reward: 10)
    "m_474d24ef",   # Empire Assests (reward: 10)
    "m_55fe2236",   # Must Join (reward: 10)
    "m_70fb9b77",   # Join Telegram Channel (reward: 10)
    "m_935bb2a2",   # Panda Crypto Casino (reward: 10)
    "m_9623f59d",   # Colour Trading Channel (reward: 10)
    "m_99498231",   # Announcement Channel (reward: 10)
    "m_a6178fb3",   # Withdraw Application And Sapport (reward: 10)
    "m_a62d7550",   # Payment Proof Channel (reward: 10)
    "m_a8fdb21d",   # Do Request Join (reward: 10)
    "m_ae3bb758",   # Crypto X Innovative (reward: 10)
    "m_b9006445",   # Russian Crypto (reward: 10)
]

# Task ID Mission (ads/link) - perlu klik link ads dulu sebelum claim
MISSION_TASK_IDS = [
    "m_b2435fe9",   # ATF X INNOVATIVE (reward: 10)
    "m_d9083736",   # Must Open And Wait Then Click On Ads (reward: 10)
    "m_ee607bbd",   # Must Open And Click The Ads (reward: 10)
]

# URL ads yang perlu diklik sebelum claim mission (bisa ditambah sesuai kebutuhan)
# Jika URL tidak diketahui, bot akan request ke server untuk mendapatkan link
ADS_URLS = {
    "m_d9083736": None,  # URL akan diambil dari mission data
    "m_ee607bbd": None,  # URL akan diambil dari mission data
    "m_b2435fe9": None,  # URL akan diambil dari mission data
}


class InnovativeUSDTBot:
    def __init__(self, init_data, account_id):
        self.init_data = init_data.strip()
        self.account_id = account_id
        self.token = None
        self.user_info = None
        self.settings = None
        self.missions = []
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
                self._log(f"Response: {response.text[:200]}", level="error")
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
                    self.missions = data.get("missions", [])

                    username = self.user_info.get("username", "Unknown")
                    telegram_id = self.user_info.get("telegramId", "")

                    self._log(f"Username: {username}", level="success")
                    self._log(f"Telegram ID: {telegram_id}")

                    # Tampilkan settings
                    if self.settings:
                        ad_reward = self.settings.get("adReward", 0)
                        max_daily_ads = self.settings.get("maxDailyAds", 0)
                        spin_cooldown = self.settings.get("spinCooldownHours", 0)
                        min_withdraw = self.settings.get("minWithdraw", 0)
                        self._log(f"Reward per iklan: {ad_reward}")
                        self._log(f"Max iklan harian: {max_daily_ads}")
                        self._log(f"Spin cooldown: {spin_cooldown} jam")
                        self._log(f"Min withdraw: {min_withdraw}")

                    # Update ADS_URLS dari mission data jika ada link
                    if self.missions:
                        self._log(f"Ditemukan {len(self.missions)} misi")
                        for mission in self.missions:
                            m_id = mission.get("id", "")
                            m_link = mission.get("link", mission.get("url", ""))
                            if m_id in ADS_URLS and m_link:
                                ADS_URLS[m_id] = m_link
                                self._log(f"  Link ads untuk {m_id}: {m_link[:50]}...")

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
        Simulasi nonton iklan adsgram (dipakai untuk watch_ad, spin, dll).
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
                    # Coba ambil record dari berbagai kemungkinan struktur response
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
            watch_time = random.uniform(1.5, 2.5)
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

    def click_ads_link(self, mission_id, url=None):
        """
        Auto-klik link ads (request GET ke URL ads) sebelum claim task mission.
        Simulasi user membuka link iklan dan menunggu beberapa detik.
        """
        # Cari URL dari ADS_URLS atau dari mission data
        ads_url = url or ADS_URLS.get(mission_id)

        # Jika URL tidak ada, cari dari self.missions
        if not ads_url and self.missions:
            for mission in self.missions:
                if mission.get("id") == mission_id:
                    ads_url = mission.get("link", mission.get("url", ""))
                    break

        if not ads_url:
            # Jika tetap tidak ada URL, simulasi adsgram sebagai pengganti
            self._log(f"    URL ads tidak ditemukan untuk {mission_id}, simulasi adsgram...", level="warning")
            return self._simulate_ad()

        self._log(f"    Mengklik link ads: {ads_url[:60]}...")

        try:
            # Request GET ke URL ads (simulasi user membuka link)
            click_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
                "Referer": "https://lexynova.com/pmads/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
            }

            response = self.session.get(
                ads_url,
                headers=click_headers,
                allow_redirects=True,
                timeout=15
            )

            if response.status_code == 200:
                self._log(f"    Link ads berhasil dibuka! (Status: {response.status_code})", level="success")
                # Jika ada redirect, log final URL
                if response.url != ads_url:
                    self._log(f"    Redirected ke: {response.url[:60]}...", level="info")
            else:
                self._log(f"    Link ads response: {response.status_code}", level="warning")

            # Tunggu beberapa detik (simulasi user membaca/melihat ads)
            wait_time = random.uniform(3, 6)
            self._log(f"    Menunggu {wait_time:.1f}s (simulasi baca iklan)...")
            time.sleep(wait_time)

            return True

        except requests.exceptions.Timeout:
            self._log(f"    Timeout saat buka link ads (tetap lanjut claim)", level="warning")
            time.sleep(2)
            return True  # Tetap return True agar claim dilanjutkan
        except requests.exceptions.ConnectionError:
            self._log(f"    Gagal koneksi ke link ads (tetap lanjut claim)", level="warning")
            time.sleep(2)
            return True
        except Exception as e:
            self._log(f"    Error klik ads: {e}", level="warning")
            time.sleep(2)
            return True  # Tetap lanjut claim

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

    def spin(self):
        """
        Spin roulette.
        Flow: simulasi adsgram → POST api.php {action: "spin"} → POST api.php {action: "claim_spin"}
        """
        self._log("Memulai spin...")

        # Simulasi adsgram sebelum spin
        self._log("  Nonton iklan sebelum spin...")
        self._simulate_ad()

        # Step 1: Spin
        self._log("  Melakukan spin...")
        try:
            api_url = f"{BASE_URL}/api.php"
            payload = {"action": "spin"}
            response = self.session.post(api_url, headers=self._base_headers(), json=payload)

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("ok") or data.get("success"):
                        result = data.get("result", data.get("reward", "?"))
                        self._log(f"  Spin berhasil! Hasil: {result}", level="success")
                    else:
                        msg = data.get("message", data.get("error", "Unknown"))
                        self._log(f"  Spin gagal: {msg}", level="warning")
                        return False
                except:
                    self._log(f"  Response spin: {response.text[:200]}", level="warning")
            else:
                self._log(f"  Spin gagal. Status: {response.status_code}", level="error")
                return False
        except Exception as e:
            self._log(f"  Error spin: {e}", level="error")
            return False

        time.sleep(random.uniform(1.5, 2.5))

        # Step 2: Claim spin reward
        self._log("  Mengklaim reward spin...")
        try:
            payload = {"action": "claim_spin"}
            response = self.session.post(api_url, headers=self._base_headers(), json=payload)

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("ok") or data.get("success"):
                        reward = data.get("reward", data.get("amount", "?"))
                        self._log(f"  Claim spin berhasil! +{reward}", level="success")
                        return True
                    else:
                        msg = data.get("message", data.get("error", "Unknown"))
                        self._log(f"  Claim spin gagal: {msg}", level="warning")
                        return False
                except:
                    self._log(f"  Response claim: {response.text[:200]}", level="warning")
                    return False
            else:
                self._log(f"  Claim spin gagal. Status: {response.status_code}", level="error")
                return False
        except Exception as e:
            self._log(f"  Error claim spin: {e}", level="error")
            return False

    def complete_twitter_tasks(self):
        """Claim semua task Twitter (hardcoded IDs)"""
        self._log(f"Memulai claim {len(TWITTER_TASK_IDS)} task Twitter...")
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

        self._log(f"Selesai! {completed}/{len(TWITTER_TASK_IDS)} task Twitter berhasil.", level="success")

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

    def complete_mission_tasks(self):
        """
        Claim semua task Mission (ads/link).
        Flow: klik link ads (GET request) → tunggu → claim task
        """
        self._log(f"Memulai claim {len(MISSION_TASK_IDS)} task Mission (ads/link)...")
        completed = 0

        for mission_id in MISSION_TASK_IDS:
            self._log(f"  Memproses mission task: {mission_id}...")

            # Step 1: Auto-klik link ads (request GET ke URL ads)
            self._log(f"  Step 1: Mengklik link ads...")
            self.click_ads_link(mission_id)

            time.sleep(random.uniform(1, 2))

            # Step 2: Claim task setelah klik ads
            self._log(f"  Step 2: Claiming task: {mission_id}...")
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

        self._log(f"Selesai! {completed}/{len(MISSION_TASK_IDS)} task Mission berhasil.", level="success")

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

            # Delay antar iklan (batas aman minimum)
            if i < max_ads - 1:
                delay = random.uniform(0.5, 1)
                self._log(f"Menunggu {delay:.1f}s sebelum iklan berikutnya...")
                time.sleep(delay)

        self._log(f"Selesai! {success_count} iklan berhasil ditonton.", level="success")

    def auto_spin(self):
        """Otomatis spin (coba beberapa kali sampai cooldown)"""
        self._log("Memulai auto spin...")
        max_spins = 5  # Coba max 5 spin
        success_count = 0

        for i in range(max_spins):
            self._log(f"\n--- Spin #{i+1}/{max_spins} ---")
            if self.spin():
                success_count += 1
            else:
                self._log("Spin gagal atau cooldown. Berhenti.", level="warning")
                break

            # Delay antar spin
            if i < max_spins - 1:
                delay = random.uniform(2, 4)
                self._log(f"Menunggu {delay:.1f}s sebelum spin berikutnya...")
                time.sleep(delay)

        self._log(f"Selesai! {success_count} spin berhasil.", level="success")

    def run(self):
        """Jalankan bot untuk satu akun"""
        print(f"\n{CYAN}{'=' * 55}{RESET}")
        self._log("Memulai bot...")

        # Step 1: Login
        if not self.login():
            self._log("Login gagal. Berhenti.", level="error")
            return

        time.sleep(random.uniform(1, 1.5))

        # Step 2: Get user data
        self.get_user_data()
        time.sleep(random.uniform(0.5, 1))

        # Step 3: Claim task Twitter
        self._log("\n--- AUTO CLAIM TWITTER TASKS ---")
        self.complete_twitter_tasks()
        time.sleep(random.uniform(1, 2))

        # Step 4: Claim task Telegram (join channel bypass)
        self._log("\n--- AUTO CLAIM TELEGRAM TASKS (JOIN CHANNEL) ---")
        self.complete_telegram_tasks()
        time.sleep(random.uniform(1, 2))

        # Step 5: Claim task Mission (auto-klik link ads dulu)
        self._log("\n--- AUTO CLAIM MISSION TASKS (KLIK ADS LINK) ---")
        self.complete_mission_tasks()
        time.sleep(random.uniform(1, 2))

        # Step 6: Auto watch ads
        self._log("\n--- AUTO WATCH ADS ---")
        self.auto_watch_ads()

        self._log("\nSemua tugas selesai untuk akun ini!", level="success")
        print(f"{CYAN}{'=' * 55}{RESET}\n")


def banner():
    os.system("cls" if os.name == "nt" else "clear")
    ascii_art = pyfiglet.figlet_format("PMADS Bot", font="slant")
    print(CYAN + BOLD + ascii_art + RESET)
    print(MAGENTA + BOLD + "Innovative USDT Bot - @Innovativeusdtbot" + RESET)
    print(YELLOW + "Auto Twitter | Auto Telegram | Auto Ads Click | Auto Watch Ads" + RESET)
    print(CYAN + "=" * 55 + RESET)
    time_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(f"{WHITE}Waktu: {time_str}{RESET}\n")


def load_data(path):
    """Baca init_data dari file data.txt"""
    if not os.path.exists(path):
        LE(f"File {path} tidak ditemukan!")
        print(f"{YELLOW}Buat file data.txt dan isi dengan init_data (satu per baris).{RESET}")
        print(f"{YELLOW}Format init_data: query_id=AAHfCGtAAAAAN8la0mrKsnD&user=...{RESET}")
        return []
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    banner()

    data_file = "data.txt"
    accounts = load_data(data_file)

    if not accounts:
        return

    LG(f"Ditemukan {len(accounts)} akun.\n")

    for i, init_data in enumerate(accounts, 1):
        bot = InnovativeUSDTBot(init_data, i)
        bot.run()

        # Delay antar akun (batas aman)
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
