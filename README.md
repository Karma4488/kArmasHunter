# kArmasHunter

`kArmasHunter` is a single-file, stdlib-only web content discovery tool for directory and file brute-forcing with optional passive crawl assistance.

## Features

- Multi-threaded directory/file discovery
- Recursive wordlist expansion into discovered directories
- Passive same-origin link extraction from HTML responses
- Wildcard/soft-404 baseline detection per directory prefix
- Status-code and content-length filtering
- Retry support and optional rotating User-Agent pool
- Report output in `txt`, `json`, or `csv`

## Installation

No external dependencies are required.

```bash
git clone https://github.com/Karma4488/kArmasHunter.git
cd kArmasHunter
python3 kArmasHunter.py --help
```

## Usage

```bash
python3 kArmasHunter.py -u <url> [options]
```

Common examples:

```bash
# Basic scan
python3 kArmasHunter.py -u https://target.tld

# Wordlist + more threads + retries
python3 kArmasHunter.py -u https://target.tld -w mylist.txt -t 30 --retries 3

# Recursive scan with passive crawl enabled (default)
python3 kArmasHunter.py -u https://target.tld -r --max-depth 2

# Disable wildcard detection and crawl
python3 kArmasHunter.py -u https://target.tld --no-wildcard --no-crawl

# Exclude status codes and content sizes
python3 kArmasHunter.py -u https://target.tld -x 404,403 --exclude-sizes 0,1234

# Write JSON report
python3 kArmasHunter.py -u https://target.tld -o report.json -f json
```

## Notes

- `--exclude` defaults to `404`.
- Specify `--exclude-sizes` with numeric content lengths (for example: `--exclude-sizes 0,1234`).
- Use this tool only against targets you own or are explicitly authorized to test.
