"""مانیتور متادیتای منابع محلی."""
import json
from config import DATA, TRUST_THRESHOLD

def main():
    path = DATA / 'configs.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    for item in data.get('source_items', []):
        item['eligible'] = item.get('trust_score', 0) >= TRUST_THRESHOLD
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
