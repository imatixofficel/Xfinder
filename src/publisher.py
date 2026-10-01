"""تولید خروجی استاتیک از داده محلی."""
import json
from config import DATA, OUTPUT

def main():
    data = json.loads((DATA / 'configs.json').read_text(encoding='utf-8'))
    OUTPUT.mkdir(exist_ok=True)
    groups = {p: [] for p in ('vless', 'vmess', 'trojan', 'ss', 'hysteria2')}
    for item in data.get('configs', []):
        groups.get(item.get('protocol', '').lower(), []).append(item.get('config', ''))
    for protocol, values in groups.items():
        (OUTPUT / f'{protocol}.txt').write_text('\n'.join(values) + '\n', encoding='utf-8')
    (OUTPUT / 'all.txt').write_text('\n'.join(x.get('config', '') for x in data.get('configs', [])) + '\n', encoding='utf-8')

if __name__ == '__main__':
    main()
