import argparse
import base64
import json
import re
import sys
import urllib.error
import urllib.request

AGENTS = ("Happ/2.0.0", "v2rayN/7.8.2", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", "curl/8.5.0")
SCHEMES = ("vless://", "vmess://", "trojan://", "ss://", "socks5://", "socks5h://", "http://")


def fetch(url: str, ua: str | None) -> str:
    last = None
    for agent in ([ua] if ua else list(AGENTS)):
        request = urllib.request.Request(url, headers={"User-Agent": agent})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read(4 * 1024 * 1024).decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            last = e
            continue
        if body.lstrip()[:200].lower().startswith(("<!doctype", "<html")):
            continue
        return body
    if last:
        raise last
    raise ValueError("the server returned a web page instead of a subscription")


def decode(body: str) -> str:
    text = body.strip().lstrip("\ufeff")
    if not text or text[0] in "{[" or "://" in text.splitlines()[0]:
        return text
    compact = re.sub(r"\s+", "", text).replace("-", "+").replace("_", "/")
    try:
        raw = base64.b64decode(compact + "=" * (-len(compact) % 4)).decode("utf-8", errors="ignore").strip()
    except ValueError:
        return text
    return raw if raw and (raw[0] in "{[" or "://" in raw) else text


def main() -> int:
    parser = argparse.ArgumentParser(description="Download a subscription link and print the servers it contains, ready to paste into the MrBeast GTFO panel (Settings, Proxy).")
    parser.add_argument("url", help="subscription link (https://...)")
    parser.add_argument("-o", "--out", help="write the result to a file instead of printing it")
    parser.add_argument("--ua", default=None, help="User-Agent sent to the provider (default: several are tried in turn)")
    args = parser.parse_args()

    try:
        text = decode(fetch(args.url, args.ua))
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"Download failed: {e}", file=sys.stderr)
        return 1

    if text[:1] in "{[":
        try:
            result = json.dumps(json.loads(text), ensure_ascii=False, indent=2)
        except ValueError:
            print("The subscription looks like JSON but cannot be parsed.", file=sys.stderr)
            return 1
        count = len(json.loads(text)) if text[0] == "[" else 1
    else:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        supported = [line for line in lines if line.lower().startswith(SCHEMES)]
        result = "\n".join(supported)
        count = len(supported)
        skipped = len(lines) - count
        if skipped:
            print(f"Skipped {skipped} entries of unsupported types.", file=sys.stderr)

    if not count:
        print("No servers found in the subscription.", file=sys.stderr)
        return 1
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(result + "\n")
        print(f"Saved {count} server(s) to {args.out}", file=sys.stderr)
    else:
        print(result)
        print(f"{count} server(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
