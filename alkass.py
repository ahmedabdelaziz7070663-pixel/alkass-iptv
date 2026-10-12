#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكربت لتوليد ملف M3U منفصل لكل قناة من قنوات الكاس القطرية
"""
import requests
import json
import sys
import os
from datetime import datetime

# ===== الإعدادات =====
API_URL = "https://shoofapi.alkass.net/Shoof/liveV3.php?state=1&userid=195364"
GROUP_NAME = "🇶🇦 قنوات الكاس القطرية"
OUTPUT_DIR = "channels"   # مجلد لحفظ ملفات القنوات
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


def safe_filename(name):
    """تحويل اسم القناة إلى اسم ملف آمن"""
    # إزالة الأحرف غير المسموحة
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in name)
    return safe.strip("-").lower()


def build_single_channel_m3u(ch):
    """بناء محتوى M3U لقناة واحدة فقط"""
    title = ch.get("title", "Unknown").strip()
    logo = ch.get("image", "").strip()
    cid = ch.get("id", "")
    url = (ch.get("body") or "").strip()

    lines = [
        "#EXTM3U",
        f"# تحديث تلقائي: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "",
        f'#EXTINF:-1 tvg-id="alkass-{cid}" '
        f'tvg-name="{title}" '
        f'tvg-logo="{logo}" '
        f'group-title="{GROUP_NAME}",{title}',
        url,
    ]
    return "\n".join(lines)


def main():
    print("🔄 جلب القنوات من API الكاس...")
    channels = fetch_channels()

    if not channels:
        print("❌ لا توجد بيانات")
        return

    # إنشاء مجلد القنوات
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # حذف الملفات القديمة
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".m3u"):
            os.remove(os.path.join(OUTPUT_DIR, f))

    count = 0
    print("\n📺 القنوات المتاحة:")
    print("=" * 60)

    for ch in channels:
        # تخطي القنوات المقفلة
        if ch.get("is_locked") is True:
            print(f"🔒 {ch.get('title')} (مقفلة - تم تخطيها)")
            continue

        url = (ch.get("body") or "").strip()
        if not url:
            print(f"⚠️  {ch.get('title')} (لا يوجد رابط)")
            continue

        # إنشاء اسم الملف من اسم القناة
        title = ch.get("title", f"channel-{ch.get('id')}")
        filename = safe_filename(title) + ".m3u"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # كتابة ملف M3U للقناة
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(build_single_channel_m3u(ch))

        print(f"✅ {title} → {filepath}")
        count += 1

    print("=" * 60)
    print(f"🎉 تم إنشاء {count} ملف M3U (كل قناة لحالها)")


if __name__ == "__main__":
    main()
