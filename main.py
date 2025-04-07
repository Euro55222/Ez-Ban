import cgi
import requests
import json
from bs4 import BeautifulSoup
from termcolor import colored
import random
import sys

class String:
    @staticmethod
    def magenta(text):
        return f"\033[35m{text}\033[0m"

def require_gem(name):
    try:
        __import__(name)
    except ImportError:
        print(f"Gem '{name}' Is Not Installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", name])
        __import__(name)

required_gems = ['cgi', 'requests', 'json', 'bs4', 'termcolor']

for gem in required_gems:
    require_gem(gem)

print(String.magenta("""
████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗   ██████╗  █████╗ ███╗   ██╗
╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝   ██╔══██╗██╔══██╗████╗  ██║
   ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝    ██████╔╝███████║██╔██╗ ██║
   ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗    ██╔══██╗██╔══██║██║╚██╗██║
   ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗██╗██████╔╝██║  ██║██║ ╚████║
   ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
                               GitHub: LeetIDA                                    
"""))

class IDA:
    def __init__(self):
        self.username = input('[?] Username: ')
        if self.username.startswith('@') or '@' in self.username:
            self.username = self.username.replace('@', '')
        self.server_log = None
        self.data_json = None
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
        print(colored("403 Forbidden Error: Your request to TikTok was blocked.", 'red'))
        print(colored("Possible actions to resolve this issue:", 'yellow'))
        print(colored("- Ensure your IP is not blacklisted by TikTok.", 'light_blue'))
        print(colored("- Try using a different IP address or proxy.", 'light_blue'))
        print(colored("- Wait and try again later if TikTok's rate limiting is causing the block.", 'light_blue'))
        sys.exit()

    def _to_json(self):
        try:
            soup = BeautifulSoup(self.server_log, 'html.parser')
            script_tag = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
            script_text = script_tag.string.strip()
            self.json_data = json.loads(script_text)['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']
        except Exception:
            print('[X] Error: Username Not Found.')
            sys.exit()

    def get_user_id(self):
        try:
            return self.json_data["user"]["id"]
        except Exception:
            return 'Unknown'

    def secUid(self):
        try:
            return self.json_data["user"]["secUid"]
        except Exception:
            return 'Unknown'

    def generate_report_url(self):
        base_url = 'https://www.tiktok.com/aweme/v2/aweme/feedback/?'

        browser_name = random.choice(['Mozilla', 'Chrome', 'Safari', 'Firefox'])
        browser_platform = random.choice(['Win32', 'Mac', 'Linux'])
        browser_version = f"5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {browser_name}/{random.randint(80, 120)}.0 Safari/537.36"
        current_region = random.choice(['US', 'UK', 'CA', 'AU', 'IN', 'BR', 'FR', 'DE', 'IT', 'ES'])
        device_id = str(random.randint(10**18, 10**19))
        is_fullscreen = str(random.choice([True, False]))
        os = random.choice(['windows', 'mac', 'linux'])
        priority_region = random.choice(['US', 'UK', 'CA', 'AU', 'IN', 'BR', 'FR', 'DE', 'IT', 'ES'])
        region = random.choice(['US', 'UK', 'CA', 'AU', 'IN', 'BR', 'FR', 'DE', 'IT', 'ES'])
        screen_height = str(random.randint(600, 1080))
        screen_width = str(random.randint(800, 1920))
        tz_name = ""
