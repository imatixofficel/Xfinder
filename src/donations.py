"""اهدای کانفیگ: ذخیره در پوشه donations/ و حذف خودکار بعد از ۲۴ ساعت.

ورودی از GitHub Issue (فرم .github/ISSUE_TEMPLATE/donate.yml) خوانده می‌شود.
متن Issue غیرمطمئن است: فقط با regex پردازش می‌شود و هرگز اجرا نمی‌شود."""
import json, os, re, sys
from datetime import datetime, timedelta, timezone
from .config import DONATIONS_DIR, DONATION_TTL_HOURS, MAX_DONATION_CONFIGS, MAX_DONATION_AD

URI = re.compile(r"(?i)\b(?:vless|vmess|trojan|ss|hysteria2)://[^\s\"'<>\\`]+")
CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f\u202a-\u202e\u2066-\u2069]")


def _now():
    return datetime.now(timezone.utc)


def clean_ad(text):
    text = CTRL.sub("", str(text or "")).replace("<", "").replace(">", "")
    text = re.sub(r"\s+", " ", text).strip()
    if text.lower() in ("_no response_", "none", "-"):
        return ""
    return text[:MAX_DONATION_AD]


def parse_issue(body):
    """بدنه‌ی Issue-form (### Heading) را به (configs, ad) تبدیل می‌کند."""
    parts = re.split(r"(?m)^###\s+", body or "")
    configs_txt, ad_txt = "", ""
    for part in parts:
        head, _, rest = part.partition("\n")
        h = head.strip().lower()
        if h.startswith("config") or "کانفیگ" in h:
            configs_txt = rest
        elif h.startswith("ad") or "متن" in h or "تبلیغ" in h:
            ad_txt = rest
    if not configs_txt:
        configs_txt = body or ""
    seen, out = set(), []
    for u in URI.findall(configs_txt):
        u = u.rstrip(".,;)]}")
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out[:MAX_DONATION_CONFIGS], clean_ad(ad_txt)


def _read_all():
    items = []
    if DONATIONS_DIR.is_dir():
        for f in sorted(DONATIONS_DIR.glob("*.json")):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                d["_file"] = f
                items.append(d)
            except Exception:
                continue
    return items


def _expires(d):
    try:
        return datetime.fromisoformat(d["expires_at"])
    except Exception:
        return _now() - timedelta(days=1)   # فایل خراب = منقضی


def load_active():
    now = _now()
    out = []
    for d in _read_all():
        if _expires(d) > now and d.get("configs"):
            out.append({k: v for k, v in d.items() if k != "_file"})
    return out


def cleanup():
    """فایل‌های منقضی را حذف می‌کند؛ تعداد حذف‌شده‌ها را برمی‌گرداند."""
    now, n = _now(), 0
    for d in _read_all():
        if _expires(d) <= now:
            try:
                d["_file"].unlink()
                n += 1
            except OSError:
                pass
    return n


def ingest(body, issue_no, user):
    configs, ad = parse_issue(body)
    if not configs:
        return False, "هیچ کانفیگ معتبری پیدا نشد (vless / vmess / trojan / ss / hysteria2)."
    for d in _read_all():       # ضد اسپم: هر کاربر هم‌زمان یک اهدای فعال
        if d.get("user") == user and _expires(d) > _now():
            return False, "شما همین الان یک اهدای فعال دارید؛ بعد از ۲۴ ساعت دوباره اهدا کنید."
    DONATIONS_DIR.mkdir(parents=True, exist_ok=True)
    now = _now()
    rec = {"id": int(issue_no), "user": str(user)[:60], "created_at": now.isoformat(),
           "expires_at": (now + timedelta(hours=DONATION_TTL_HOURS)).isoformat(),
           "ad": ad, "configs": configs}
    (DONATIONS_DIR / f"{now:%Y%m%dT%H%M%S}-{int(issue_no)}.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    return True, f"اهدا ثبت شد و تا {DONATION_TTL_HOURS} ساعت بعد از تست موفق نمایش داده می‌شود. سپاس!"


def ingest_json(payload_json, run_id):
    """اهدای مستقیم از سایت (Cloudflare Worker -> repository_dispatch). ورودی دوباره اعتبارسنجی می‌شود."""
    try:
        p = json.loads(payload_json or "{}")
    except Exception:
        return False, "ورودی نامعتبر است."
    cfgs = p.get("configs") if isinstance(p, dict) else None
    text = "\n".join(str(c) for c in cfgs[:MAX_DONATION_CONFIGS * 2]) if isinstance(cfgs, list) else ""
    found = []
    for u in URI.findall(text):
        u = u.rstrip(".,;)]}")
        if u not in found:
            found.append(u)
    user = re.sub(r"[^A-Za-z0-9_-]", "", str(p.get("user", "web")))[:40] or "web"
    return ingest("### Configs\n" + "\n".join(found[:MAX_DONATION_CONFIGS]) + "\n\n### Ad\n" + clean_ad(p.get("ad", "")),
                  int(run_id or 0), "web-" + user)


def _gh_out(**kv):
    path = os.getenv("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            for k, v in kv.items():
                f.write(f"{k}={str(v).replace(chr(10), ' ')}\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "ingest":
        ok, msg = ingest(os.getenv("ISSUE_BODY", ""), os.getenv("ISSUE_NUMBER", "0") or 0, os.getenv("ISSUE_USER", "anon"))
        print(ok, msg)
        _gh_out(ok=str(ok).lower(), message=msg)
    elif cmd == "ingest-json":
        ok, msg = ingest_json(os.getenv("DONATION_JSON", ""), os.getenv("RUN_ID", "0") or 0)
        print(ok, msg)
        _gh_out(ok=str(ok).lower(), message=msg)
    elif cmd == "cleanup":
        print("removed", cleanup())
    else:
        print("usage: python -m src.donations ingest|cleanup")
