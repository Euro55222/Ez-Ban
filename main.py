import os
import sys
import time
import json
import random
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

class IDA:
    def __init__(self):
        self.username = input(f"{Fore.LIGHTBLUE_EX}[?] Username: {Style.RESET_ALL}")
        self.username = self.username.lstrip('@')  # Remove '@' if present
        self.server_log = None
        self.json_data = None
        self.admin()

    def admin(self):
        self.send_request()
        self._to_json()
        self.output()

    def send_request(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 IDA'
        }
        response = requests.get(f"https://www.tiktok.com/@{self.username}", headers=headers)
        if response.status_code == 403:
            self.handle_forbidden_error()
        else:
            self.server_log = response.text

    def handle_forbidden_error(self):
        print(f"{Fore.RED}403 Forbidden Error: Your request to TikTok was blocked.")
        print(f"{Fore.YELLOW}Possible actions to resolve this issue:")
        print(f"{Fore.LIGHTBLUE_EX}- Ensure your IP is not blacklisted by TikTok.")
        print(f"{Fore.LIGHTBLUE_EX}- Try using a different IP address or proxy.")
        print(f"{Fore.LIGHTBLUE_EX}- Wait and try again later if TikTok's rate limiting is causing the block.")
        sys.exit()

    def _to_json(self):
        try:
            soup = BeautifulSoup(self.server_log, 'html.parser')
            script_tag = soup.find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
            script_text = script_tag.text.strip()
            self.json_data = json.loads(script_text)['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']
        except Exception as e:
            print(f"{Fore.RED}[X] Error: Username Not Found.")
            sys.exit()

    def get_user_id(self):
        try:
            return self.json_data["user"]["id"]
        except KeyError:
            return 'Unknown'

    def secUid(self):
        try:
            return self.json_data["user"]["secUid"]
        except KeyError:
            return 'Unknown'

    def generate_report_url(self):
        base_url = 'https://www.tiktok.com/aweme/v2/aweme/feedback/?'

        params = {
            "aid": random.choice([
                '9101', '91011', '9009', '90093', '90097', '90095', '90064',
                '90061', '90063', '9006', '9008', '90081', '90082', '9007'
            ]),
            "app_language": "en",
            "app_name": "tiktok_web",
            "browser_language": "en-US",
            "browser_name": random.choice(['Mozilla', 'Chrome', 'Safari', 'Firefox']),
            "browser_online": "true",
            "browser_platform": random.choice(['Win32', 'Mac', 'Linux']),
            "browser_version": f"5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                               f"{random.choice(['Mozilla', 'Chrome', 'Safari', 'Firefox'])}/{random.randint(80, 120)}.0 Safari/537.36",
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "current_region": random.choice(['US', 'UK', 'CA', 'AU', 'IN', 'BR', 'FR', 'DE', 'IT', 'ES']),
            "device_id": str(random.randint(10 ** 18, 10 ** 19)),
            "device_platform": "web_pc",
            "focus_state": "true",
            "from_page": "user",
            "history_len": "1",
            "is_fullscreen": str(random.choice([True, False])).lower(),
            "is_page_visible": "true",
            "lang": "en",
            "nickname": quote_plus(self.username),
            "object_id": self.get_user_id(),
            "os": random.choice(['windows', 'mac', 'linux']),
            "priority_region": random.choice(['US', 'UK', 'CA', 'AU', 'IN', 'BR', 'FR', 'DE', 'IT', 'ES']),
            "reason": "9010",
            "referer": "https://www.tiktok.com/",
            "region": random.choice(['US', 'UK', 'CA', 'AU', 'IN', 'BR', 'FR', 'DE', 'IT', 'ES']),
            "report_type": "user",
            "reporter_id": self.get_user_id(),
            "root_referer": "https://www.tiktok.com/",
            "screen_height": str(random.randint(600, 1080)),
            "screen_width": str(random.randint(800, 1920)),
            "secUid": self.secUid(),
            "target": self.get_user_id(),
            "tz_name": random.choice([
                'America/New_York', 'Europe/London', 'Asia/Tokyo',
                'Australia/Sydney', 'Asia/Kolkata', 'America/Los_Angeles'
            ]),
            "webcast_language": random.choice(['en', 'es', 'fr', 'de', 'ja', 'pt', 'it', 'ru', 'ar', 'hi'])
        }

        return base_url + "&".join(f"{k}={v}" for k, v in params.items())

    def output(self):
        report_url = self.generate_report_url()
        proxies = self.load_proxies_from_file('proxy.txt')

        if not proxies:
            print(f"{Fore.RED}[X] Proxy File Is Empty.")
            sys.exit()

        for proxy in proxies:
            try:
                current_time = time.strftime('%H:%M:%S')
                response = requests.post(report_url, proxies={"http": proxy, "https": proxy}, timeout=2)
                if response.text:
                    response_body = response.json()
                    if response_body.get('status_code') == 0:
                        print(f"{Fore.RED}[{current_time}] {Fore.GREEN}Proxy: {proxy} Report Sent To {self.username}")
                    else:
                        print(f"{Fore.RED}[{current_time}] {Fore.YELLOW}Proxy: {proxy} Report Failed. Response: {response.text}")
                else:
                    print(f"{Fore.RED}[{current_time}] {Fore.RED}Proxy: {proxy} Empty or Invalid Response")
            except Exception as e:
                print(f"{Fore.RED}[X] Something Went Wrong: {e}")
                input(f"{Fore.RED}Press Enter to close the program")
                sys.exit()
            time.sleep(3)

    def load_proxies_from_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"{Fore.RED}Proxy File Does Not Exist. Creating One...")
            with open(file_path, 'w') as f:
                f.write("")
            sys.exit()

        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f.readlines()]
        if not proxies:
            print(f"{Fore.RED}Proxy File Is Empty.")
            sys.exit()

        return proxies


if __name__ == "__main__":
    IDA()
