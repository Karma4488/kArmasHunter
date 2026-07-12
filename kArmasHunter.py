#!/usr/bin/env python3
"""
kArmasHunter - Web Content Discovery Tool
Dirsearch/Dirhunt-style directory & file brute-forcer with passive crawl assist.
Single-file, stdlib-only. Termux / Kali compatible.

We Are Legion. We Do Not Forget. We Do Not Forgive.
"""

import sys
import os
import time
import json
import ssl
import socket
import threading
import queue
import random
import csv
from datetime import datetime
from urllib import request as urlrequest
from urllib.parse import urljoin, urlsplit
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser

# ============================================================
#  COLORS
# ============================================================
class C:
    G = "\033[92m"
    DG = "\033[32m"
    R = "\033[91m"
    Y = "\033[93m"
    B = "\033[94m"
    M = "\033[95m"
    CY = "\033[96m"
    W = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

# ============================================================
#  MATRIX RAIN INTRO
# ============================================================
def matrix_rain(duration=1.6):
    try:
        cols = os.get_terminal_size().columns
    except OSError:
        cols = 80
    chars = "01ｱｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾅﾆﾇﾈﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜkArma"
    drops = [random.randint(-20, 0) for _ in range(cols)]
    start = time.time()
    while time.time() - start < duration:
        line = ""
        for i in range(cols):
            if drops[i] >= 0 and random.random() > 0.15:
                line += C.G + random.choice(chars)
            else:
                line += " "
            drops[i] += 1
            if drops[i] > 30 and random.random() > 0.95:
                drops[i] = random.randint(-10, 0)
        sys.stdout.write("\r" + line[:cols])
        sys.stdout.flush()
        time.sleep(0.04)
    sys.stdout.write("\r" + " " * cols + "\r")
    print(C.RESET)

# ============================================================
#  BANNER
# ============================================================
SKULL = r"""
        .co0OKKKKKKKKKK0oc.
     .oKKKKKKKKKKKKKKKKKKKKo.
    cKKKKKKKKKKKKKKKKKKKKKKKc
   0KKKKKKKKKKKKKKKKKKKKKKKK0
  0KKKK.       KKKK.       KKK0
  KKKK.  .oOKo.KKKK.  .oOKo. KKK
  KKKK.  OKKKKOKKKK.  OKKKKO .KK
  KKKK.  .oOKo.KKKK.  .oOKo. KKK
  0KKKK.       KKKK.       KKK0
   KKKKKKo.  .oKKKKo.  .oKKKKK
    cKKKKKKKKKKKKKKKKKKKKKKKc
     .oKKKK0OxoodxO0KKKKKo.
        'cccccccccccccc'
"""

def print_banner():
    print(C.G + SKULL + C.RESET)
    title = r"""
  _  _   ____                          _   _             _
 | |/ /  / _  \ _ __ _ __ ___   __ _ ___| | | |_   _ _ __ | |_ ___ _ __
 | ' /  | |_| || '__| '_ ` _ \ / _` / __| |_| | | | | '_ \| __/ _ \ '__|
 | . \  |  _  || |  | | | | | | (_| \__ \  _  | |_| | | | | ||  __/ |
 |_|\_\ |_| |_||_|  |_| |_| |_|\__,_|___/_| |_|\__,_|_| |_|\__\___|_|
"""
    print(C.DG + C.BOLD + title + C.RESET)
    print(C.G + "         [ Content Discovery :: dirsearch/dirhunt hybrid ]" + C.RESET)
    print(C.DIM + C.G + "              We Are Legion. We Do Not Forget. We Do Not Forgive." + C.RESET)
    print(C.G + "-" * 72 + C.RESET)

# ============================================================
#  AUTHORIZATION GATE
# ============================================================
VALID_PHRASES = {"I HAVE AUTHORIZATION", "I AGREE", "WE_ARE_LEGION"}

def authorization_gate():
    print(C.Y + C.BOLD + "\n  [!] AUTHORIZATION REQUIRED" + C.RESET)
    print(C.W + "  This tool sends active HTTP requests (directory/file brute-forcing)")
    print("  against a target host. Only use this against systems you own or")
    print("  are explicitly authorized to test.\n" + C.RESET)
    print(C.DIM + "  Type one of: \"I HAVE AUTHORIZATION\", \"I AGREE\", or \"WE_ARE_LEGION\"" + C.RESET)
    resp = input(C.G + "  > " + C.RESET).strip()
    if resp.upper() not in {p.upper() for p in VALID_PHRASES}:
        print(C.R + "\n  [x] Authorization not confirmed. Exiting." + C.RESET)
        sys.exit(1)
    print(C.G + "  [OK] Authorization confirmed.\n" + C.RESET)

# ============================================================
#  DEFAULT WORDLISTS (small built-in, user can supply their own)
# ============================================================
DEFAULT_WORDLIST = [
    "admin", "administrator", "login", "backup", "backups", "old", "test",
    "dev", "staging", "config", "configs", ".env", ".env.bak", ".git",
    ".git/config", ".svn", "wp-admin", "wp-login.php", "wp-content",
    "wp-includes", "api", "api/v1", "api/v2", "uploads", "images", "img",
    "assets", "static", "js", "css", "includes", "inc", "lib", "vendor",
    "node_modules", "logs", "log", "tmp", "temp", "cache", "database",
    "db", "sql", "dump", "dump.sql", "backup.sql", "backup.zip",
    "site.zip", "www.zip", "web.config", ".htaccess", ".htpasswd",
    "robots.txt", "sitemap.xml", "crossdomain.xml", "phpinfo.php",
    "info.php", "test.php", "readme.md", "README.md", "CHANGELOG.md",
    "LICENSE", "package.json", "composer.json", "Dockerfile",
    "docker-compose.yml", "Gemfile", "requirements.txt", ".DS_Store",
    "server-status", "server-info", "console", "actuator", "swagger",
    "swagger-ui.html", "graphql", "graphiql", "debug", "trace",
    "admin.php", "administrator.php", "panel", "cpanel", "webmail",
    "mail", "portal", "dashboard", "manage", "management", "private",
    "secret", "secrets", "credentials", "keys", "key", "cert", "certs",
    "ssl", "auth", "oauth", "sso", "user", "users", "account", "accounts",
    "profile", "settings", "setup", "install", "installer", "update",
    "upgrade", "migrate", "migration", "migrations", "scripts", "bin",
    "sbin", "shell", "cgi-bin", "cgi", "phpmyadmin", "adminer",
    "elastic", "kibana", "grafana", "jenkins", "gitlab", "jira",
]

COMMON_EXTENSIONS = ["", ".php", ".html", ".htm", ".txt", ".bak", ".zip",
                     ".json", ".xml", ".asp", ".aspx", ".jsp", ".old", ".log"]

# dirsearch-style rotating User-Agent pool (used with --random-agent)
RANDOM_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
]

# ============================================================
#  LINK EXTRACTOR (passive crawl assist - dirhunt-style)
# ============================================================
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        attr_map = dict(attrs)
        for key in ("href", "src", "action"):
            if key in attr_map and attr_map[key]:
                self.links.add(attr_map[key])

# ============================================================
#  CORE SCANNER
# ============================================================
class KArmasHunter:
    def __init__(self, base_url, wordlist, extensions, threads=20, timeout=6,
                 status_filter=None, exclude_status=None, recursive=False,
                 max_depth=2, user_agent=None, delay=0, crawl=True,
                 follow_redirects=False, out_file=None, out_format="txt",
                 random_agent=False, retries=1, exclude_sizes=None,
                 detect_wildcard=True):
        self.base_url = base_url.rstrip("/") + "/"
        self.wordlist = wordlist
        self.extensions = extensions
        self.threads = threads
        self.timeout = timeout
        self.status_filter = status_filter
        self.exclude_status = exclude_status or [404]
        self.recursive = recursive
        self.max_depth = max_depth
        self.user_agent = user_agent or "kArmasHunter/1.0 (+recon)"
        self.delay = delay
        self.crawl = crawl
        self.follow_redirects = follow_redirects
        self.out_file = out_file
        self.out_format = out_format
        self.random_agent = random_agent
        self.retries = max(1, retries)
        self.exclude_sizes = {str(size) for size in exclude_sizes} if exclude_sizes else set()

        self.detect_wildcard = detect_wildcard
        # per-prefix baseline of "soft 404" (status, length) signatures, dirsearch-style
        self.wildcard_baseline = {}

        self.q = queue.Queue()
        self.results = []
        self.lock = threading.Lock()
        self.visited_dirs = set()
        self.crawled_links = set()
        self.stop_flag = threading.Event()
        self.total_scanned = 0
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

    # ---------- HTTP ----------
    def _request(self, url):
        ua = random.choice(RANDOM_USER_AGENTS) if self.random_agent else self.user_agent
        attempt = 0
        while attempt < self.retries:
            attempt += 1
            req = urlrequest.Request(url, method="GET")
            req.add_header("User-Agent", ua)
            try:
                opener_args = {"timeout": self.timeout, "context": self.ssl_ctx}
                with urlrequest.urlopen(req, **opener_args) as resp:
                    code = resp.getcode()
                    body = resp.read(65536)
                    length = resp.headers.get("Content-Length", str(len(body)))
                    return code, length, body
            except HTTPError as e:
                body = b""
                try:
                    body = e.read(4096)
                except Exception:
                    pass
                return e.code, e.headers.get("Content-Length", str(len(body))), body
            except (URLError, socket.timeout, ConnectionError, TimeoutError):
                if attempt >= self.retries:
                    return None, None, None
                time.sleep(0.3 * attempt)
            except Exception:
                return None, None, None
        return None, None, None

    # ---------- dirsearch-style wildcard / false-positive detection ----------
    def _detect_wildcard_for_prefix(self, prefix):
        """Probe a random, near-certainly-nonexistent path to fingerprint the
        server's 'soft 404' response (a page that returns 200 for anything).
        Any real result matching this signature is treated as a false positive."""
        if not self.detect_wildcard:
            return
        with self.lock:
            if self.wildcard_baseline.get(prefix, False) is not False:
                return
        probe = f"{prefix}kArmasHunter-nonexistent-{random.randint(100000,999999)}.html"
        url = urljoin(self.base_url, probe)
        code, length, _ = self._request(url)
        with self.lock:
            if code is not None:
                self.wildcard_baseline[prefix] = (code, length)
            else:
                self.wildcard_baseline[prefix] = None

    def _is_wildcard_match(self, prefix, code, length):
        with self.lock:
            baseline = self.wildcard_baseline.get(prefix)
        if not baseline:
            return False
        b_code, b_length = baseline
        return code == b_code and length == b_length

    # ---------- Status coloring ----------
    @staticmethod
    def _status_color(code):
        if code is None:
            return C.DIM
        if 200 <= code < 300:
            return C.G
        if 300 <= code < 400:
            return C.CY
        if 400 <= code < 500:
            return C.Y
        return C.R

    def _passes_filter(self, code, length=None):
        if code is None:
            return False
        if length is not None and str(length) in self.exclude_sizes:
            return False
        if self.status_filter:
            return code in self.status_filter
        if self.exclude_status:
            return code not in self.exclude_status
        return True

    # ---------- Worker ----------
    def _worker(self):
        while not self.stop_flag.is_set():
            try:
                path, depth = self.q.get(timeout=1)
            except queue.Empty:
                return
            try:
                prefix = path.rsplit("/", 1)[0] + "/" if "/" in path else ""
                if self.detect_wildcard:
                    with self.lock:
                        if prefix not in self.wildcard_baseline:
                            self.wildcard_baseline[prefix] = False
                            need_probe = True
                        else:
                            need_probe = False
                    if need_probe:
                        self._detect_wildcard_for_prefix(prefix)

                url = urljoin(self.base_url, path)
                code, length, body = self._request(url)
                with self.lock:
                    self.total_scanned += 1

                is_wildcard = self.detect_wildcard and self._is_wildcard_match(prefix, code, length)

                if not is_wildcard and self._passes_filter(code, length):
                    with self.lock:
                        self.results.append({
                            "url": url, "status": code, "length": length,
                            "depth": depth
                        })
                    col = self._status_color(code)
                    sys.stdout.write(
                        f"\r{' '*100}\r{col}[{code}]{C.RESET} "
                        f"{C.DIM}({length} bytes){C.RESET}  {url}\n"
                    )
                    sys.stdout.flush()

                    # recursive descent into found directories
                    if self.recursive and path.endswith("/") and depth < self.max_depth:
                        with self.lock:
                            is_new_dir = path not in self.visited_dirs
                            if is_new_dir:
                                self.visited_dirs.add(path)
                        if is_new_dir:
                            self._enqueue_wordlist(path, depth + 1)

                    # passive crawl: pull links out of HTML responses
                    if self.crawl and body and code and 200 <= code < 300:
                        self._extract_and_queue(url, body, depth)

                if self.delay:
                    time.sleep(self.delay)
            finally:
                self.q.task_done()
                self._progress()

    def _progress(self):
        with self.lock:
            scanned = self.total_scanned
            found = len(self.results)
        sys.stdout.write(
            f"\r{C.DIM}  scanned: {scanned}  |  found: {found}  |  queue: {self.q.qsize()}   {C.RESET}"
        )
        sys.stdout.flush()

    def _extract_and_queue(self, url, body, depth):
        try:
            text = body.decode("utf-8", errors="ignore")
        except Exception:
            return
        parser = LinkParser()
        try:
            parser.feed(text)
        except Exception:
            return
        base_netloc = urlsplit(self.base_url).netloc
        for link in parser.links:
            full = urljoin(url, link)
            parts = urlsplit(full)
            if parts.netloc != base_netloc:
                continue
            with self.lock:
                if full in self.crawled_links:
                    continue
                self.crawled_links.add(full)

            rel = parts.path.lstrip("/")
            if not rel:
                continue
            self.q.put((rel, depth))

            if self.recursive and parts.path.endswith("/") and depth < self.max_depth:
                dir_path = rel if rel.endswith("/") else rel + "/"
                with self.lock:
                    is_new_dir = dir_path not in self.visited_dirs
                    if is_new_dir:
                        self.visited_dirs.add(dir_path)
                if is_new_dir:
                    self._enqueue_wordlist(dir_path, depth + 1)

    # ---------- Queue building ----------
    def _enqueue_wordlist(self, prefix, depth):
        for word in self.wordlist:
            for ext in self.extensions:
                candidate = f"{prefix}{word}{ext}"
                self.q.put((candidate, depth))

    # ---------- Run ----------
    def run(self):
        self._enqueue_wordlist("", 0)
        total_jobs = self.q.qsize()
        print(C.G + f"  [*] Target     : {self.base_url}" + C.RESET)
        print(C.G + f"  [*] Wordlist   : {len(self.wordlist)} entries x {len(self.extensions)} extensions" + C.RESET)
        print(C.G + f"  [*] Queue size : {total_jobs}" + C.RESET)
        print(C.G + f"  [*] Threads    : {self.threads}" + C.RESET)
        print(C.G + f"  [*] Recursive  : {self.recursive} (max depth {self.max_depth})" + C.RESET)
        print(C.G + f"  [*] Crawl mode : {self.crawl}" + C.RESET)
        print(C.G + f"  [*] Retries    : {self.retries}   Random-UA: {self.random_agent}" + C.RESET)
        print(C.G + f"  [*] Wildcard FP detection : {self.detect_wildcard}" + C.RESET)
        if self.exclude_sizes:
            print(C.G + f"  [*] Excluded sizes : {', '.join(self.exclude_sizes)}" + C.RESET)
        print(C.G + "-" * 72 + C.RESET)

        workers = []
        for _ in range(self.threads):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            workers.append(t)

        try:
            self.q.join()
        except KeyboardInterrupt:
            print(C.R + "\n\n  [!] Interrupted by user. Stopping workers..." + C.RESET)
            self.stop_flag.set()
            while not self.q.empty():
                try:
                    self.q.get_nowait()
                    self.q.task_done()
                except queue.Empty:
                    break

        print("\n" + C.G + "-" * 72 + C.RESET)
        print(C.G + C.BOLD + f"  [+] Scan complete. {len(self.results)} paths found "
              f"out of {self.total_scanned} requests." + C.RESET)

        if self.out_file:
            self._write_report()

    # ---------- Report ----------
    def _write_report(self):
        results_sorted = sorted(self.results, key=lambda r: r["url"])
        if self.out_format == "json":
            with open(self.out_file, "w") as f:
                json.dump(results_sorted, f, indent=2)
        elif self.out_format == "csv":
            with open(self.out_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["url", "status", "length", "depth"])
                writer.writeheader()
                writer.writerows(results_sorted)
        else:
            with open(self.out_file, "w") as f:
                f.write(f"kArmasHunter report - {datetime.now().isoformat()}\n")
                f.write(f"Target: {self.base_url}\n")
                f.write("-" * 60 + "\n")
                for r in results_sorted:
                    f.write(f"[{r['status']}] {r['url']} ({r['length']} bytes)\n")
        print(C.G + f"  [+] Report written to {self.out_file}" + C.RESET)

# ============================================================
#  CLI
# ============================================================
def load_wordlist(path):
    if not path:
        return DEFAULT_WORDLIST
    if not os.path.isfile(path):
        print(C.R + f"  [x] Wordlist not found: {path}" + C.RESET)
        sys.exit(1)
    with open(path, "r", errors="ignore") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def parse_status_list(s):
    if not s:
        return None
    out = []
    for chunk in s.split(","):
        chunk = chunk.strip()
        if "-" in chunk:
            a, b = chunk.split("-")
            out.extend(range(int(a), int(b) + 1))
        elif chunk:
            out.append(int(chunk))
    return out

def print_help():
    print(f"""{C.G}
  Usage: python3 kArmasHunter.py -u <url> [options]

  Required:
    -u, --url URL           Target base URL (e.g. https://example.com)

  Wordlist / Extensions:
    -w, --wordlist FILE     Path to wordlist file (default: built-in list of {len(DEFAULT_WORDLIST)} words)
    -e, --extensions LIST   Comma-separated extensions (default: {','.join(x or '(none)' for x in COMMON_EXTENSIONS)})

  Scan behavior:
    -t, --threads N         Number of worker threads (default: 20)
    -r, --recursive         Recurse into discovered directories
    --max-depth N           Max recursion depth (default: 2)
    --timeout N             Request timeout in seconds (default: 6)
    --delay N               Delay between requests per thread, seconds (default: 0)
    --no-crawl              Disable passive link extraction from responses
    --retries N             Retry attempts per request on connection failure (default: 1)
    --random-agent          Rotate through a pool of realistic browser User-Agents

  Filtering (dirsearch-style):
    -s, --status LIST       Only show these status codes (e.g. 200,301-302)
    -x, --exclude LIST      Exclude these status codes (default: 404)
    --exclude-sizes LIST    Exclude responses with these Content-Length values (e.g. 0,1234)
    --no-wildcard           Disable automatic soft-404 / wildcard false-positive detection
                            (by default, a random nonexistent path is probed per directory
                            and matching responses are auto-filtered out)

  Output:
    -o, --output FILE       Write results to file
    -f, --format FORMAT     txt | json | csv (default: txt)

  Example:
    python3 kArmasHunter.py -u https://target.tld -w mylist.txt -r -t 30 -o report.json -f json
{C.RESET}""")

def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args or not args:
        matrix_rain(0.8)
        print_banner()
        print_help()
        sys.exit(0)

    url = None
    wordlist_path = None
    extensions = None
    threads = 20
    recursive = False
    max_depth = 2
    timeout = 6
    delay = 0
    crawl = True
    status_filter = None
    exclude_status = "404"
    out_file = None
    out_format = "txt"
    random_agent = False
    retries = 1
    exclude_sizes = None
    detect_wildcard = True

    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-u", "--url"):
            i += 1; url = args[i]
        elif a in ("-w", "--wordlist"):
            i += 1; wordlist_path = args[i]
        elif a in ("-e", "--extensions"):
            i += 1; extensions = [e if e.startswith(".") or e == "" else "." + e
                                   for e in args[i].split(",")]
        elif a in ("-t", "--threads"):
            i += 1; threads = int(args[i])
        elif a in ("-r", "--recursive"):
            recursive = True
        elif a == "--max-depth":
            i += 1; max_depth = int(args[i])
        elif a == "--timeout":
            i += 1; timeout = int(args[i])
        elif a == "--delay":
            i += 1; delay = float(args[i])
        elif a == "--no-crawl":
            crawl = False
        elif a in ("-s", "--status"):
            i += 1; status_filter = args[i]
        elif a in ("-x", "--exclude"):
            i += 1; exclude_status = args[i]
        elif a in ("-o", "--output"):
            i += 1; out_file = args[i]
        elif a in ("-f", "--format"):
            i += 1; out_format = args[i]
        elif a == "--random-agent":
            random_agent = True
        elif a == "--retries":
            i += 1; retries = int(args[i])
        elif a == "--exclude-sizes":
            i += 1; exclude_sizes = [s.strip() for s in args[i].split(",") if s.strip()]
        elif a == "--no-wildcard":
            detect_wildcard = False
        else:
            print(C.R + f"  [x] Unknown argument: {a}" + C.RESET)
            sys.exit(1)
        i += 1

    if not url:
        print(C.R + "  [x] -u/--url is required" + C.RESET)
        sys.exit(1)
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    matrix_rain(1.4)
    print_banner()
    authorization_gate()

    wl = load_wordlist(wordlist_path)
    ext = extensions or COMMON_EXTENSIONS

    hunter = KArmasHunter(
        base_url=url,
        wordlist=wl,
        extensions=ext,
        threads=threads,
        timeout=timeout,
        status_filter=parse_status_list(status_filter),
        exclude_status=parse_status_list(exclude_status),
        recursive=recursive,
        max_depth=max_depth,
        delay=delay,
        crawl=crawl,
        out_file=out_file,
        out_format=out_format,
        random_agent=random_agent,
        retries=retries,
        exclude_sizes=exclude_sizes,
        detect_wildcard=detect_wildcard,
    )
    hunter.run()

if __name__ == "__main__":
    main()
