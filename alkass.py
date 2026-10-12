#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكربت لتوليد ملف M3U لقنوات الكاس القطرية تلقائياً
"""
import requests
import json
import sys
from datetime import datetime

# ===== الإعدادات =====
API_URL = "https://shoofapi.alkass.net/Shoof/liveV3.php?state=1&userid=195364"
OUTPUT_FILE = "alkass.m3u"
GROUP_NAME = "🇶🇦 قنوات الكاس القطرية"
USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"


def fetch_channels():
    """جلب القنوات من API الكاس"""
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
        print(f"❌ خطأ في جلب البيانات: {e}", file=sys.stderr)
        return []


def build_m3u(channels):
    """بناء محتوى ملف M3U"""
    lines = ["#EXTM3U"]
    lines.append(f"# تحديث تلقائي: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append("")

    count = 0
    for ch in channels:
        # تخطي القنوات المقفلة
        if ch.get("is_locked") is True:
            continue

        url = (ch.get("body") or "").strip()
        if not url:
            continue

        # دعم link2 كبديل
        if not url:
            url = (ch.get("link2") or "").strip()
            if not url:
                continue

        title = ch.get("title", "Unknown").strip()
        logo = ch.get("image", "").strip()
        cid = ch.get("id", "")
        webname = ch.get("webname", "")

        lines.append(
            f'#EXTINF:-1 tvg-id="alkass-{cid}" '
            f'tvg-name="{title}" '
            f'tvg-logo="{logo}" '
            f'group-title="{GROUP_NAME}",{title}'
        )
        lines.append(url)
        count += 1

    print(f"✅ تم توليد {count} قناة")
    return "\n".join(lines)


def main():
    print("🔄 جلب القنوات من API الكاس...")
    channels = fetch_channels()

    if not channels:
        print("❌ لا توجد بيانات، سيتم إنشاء ملف فارغ")
        channels = []

    m3u_content = build_m3u(channels)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"✅ تم إنشاء الملف: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
