"""اعتبارسنجی ساختاری داده محلی.

تست فعال endpointهای پروکسی و اجرای Core در این نسخه انجام نمی‌شود.
"""
import json
from config import DATA

REQUIRED = {'protocol', 'server', 'port', 'config'}

def validate_record(item):
    return REQUIRED.issubset(item)

def main():
    path = DATA / 'configs.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    valid = [x for x in data.get('configs', []) if validate_record(x)]
    data.setdefault('stats', {})['total'] = len(valid)
    data['stats']['alive'] = len(valid)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    return len(valid)

if __name__ == '__main__':
    print(f'Valid local records: {main()}')
