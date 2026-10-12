#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكربت مُحسّن لتوليد M3U لقنوات الكاس مع دعم Referer و User-Agent
"""
import requests
import sys
import os
from datetime import datetime

API_URL = "https://shoofapi.alkass.net/Shoof/liveV3.php?state=1&userid=195364"
OUTPUT_FILE = "alkass.m3u"
GROUP_NAME = "🇶🇦 قنوات الكاس القطرية"
USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36"


def fetch_channels():
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Referer": "https://www.alkass.net/",
    }
    try:
        r = requests.get(API_URL, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ خطأ: {e}", file=sys.stderr)
        return []


def build_m3u(channels):
    lines = ["#EXTM3U"]
    lines.append(f"# تحديث: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append("")

    count = 0
    for ch in channels:
        if ch.get("is_locked") is True:
            continue

        url = (ch.get("body") or "").strip()
        if not url:
            continue

        title = ch.get("title", "Unknown")
        logo = ch.get("image", "")
        cid = ch.get("id", "")

        # ✅ إضافة Referer و User-Agent لكل قناة (مهم!)
        lines.append(
            f'#EXTINF:-1 tvg-id="alkass-{cid}" '
            f'tvg-name="{title}" '
            f'tvg-logo="{logo}" '
            f'group-title="{GROUP_NAME}",{title}'
        )
        lines.append("#EXTVLCOPT:http-referrer=https://www.alkass.net/")
        lines.append(f"#EXTVLCOPT:http-user-agent={USER_AGENT}")
        lines.append(url)
        count += 1

    print(f"✅ تم توليد {count} قناة")
    return "\n".join(lines)


def main():
    channels = fetch_channels()
    if not channels:
        print("❌ لا توجد بيانات")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(build_m3u(channels))

    print(f"✅ تم إنشاء {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
