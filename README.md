# kArmasHunter

python3 kArmasHunter.py -u https://target.tld -w mylist.txt --no-wildcard -t 30

python3 kArmasHunter.py -u https://target.tld -w mylist.txt --no-wildcard --no-crawl -x "" -t 30


--random-agent — rotates through a pool of realistic browser UAs per request
--retries N — retry failed connections with backoff instead of dying on one timeout
--exclude-sizes LIST — filter out responses by Content-Length, dirsearch-style
--no-wildcard — disable the false-positive detection if you want raw brute-force behavior


"""
kArmasHunter - Web Content Discovery Tool
Dirsearch/Dirhunt-style directory & file brute-forcer with passive crawl assist.
Single-file, stdlib-only. Termux / Kali compatible.

We Are Legion. We Do Not Forget. We Do Not Forgive.
"""
