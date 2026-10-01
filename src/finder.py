"""Finder محلی.

برای جلوگیری از جمع‌آوری خودکار endpointهای پروکسی عمومی، این نسخه فقط
رکوردهای موجود در data/configs.json را می‌خواند و هیچ URL/کانال زنده‌ای را
crawl نمی‌کند.
"""
import json
from config import DATA

def main():
    data = json.loads((DATA / 'configs.json').read_text(encoding='utf-8'))
    return len(data.get('configs', []))

if __name__ == '__main__':
    print(f'Local records: {main()}')
