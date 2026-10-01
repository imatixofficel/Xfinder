"""محاسبه Trust Score برای متادیتای منابع."""
WEIGHTS = {
    'has_http_test': 40,
    'update_frequency': 20,
    'config_count': 15,
    'avg_ping_quality': 15,
    'success_rate': 10,
}

def score(*, has_http_test=False, update_frequency=0, config_count=0,
          avg_ping_quality=0, success_rate=0):
    points = 0
    points += WEIGHTS['has_http_test'] if has_http_test else 0
    points += min(20, max(0, update_frequency))
    points += min(15, round(config_count / 20 * 15))
    points += min(15, round(max(0, 1 - avg_ping_quality / 500) * 15))
    points += min(10, round(max(0, min(1, success_rate)) * 10))
    return int(points)
