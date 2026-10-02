// Cloudflare Worker: دریافت اهدا از سایت و ارسال به GitHub (repository_dispatch).
// توکن GitHub فقط اینجا (Secret) نگه‌داری می‌شود؛ هرگز در سایت قرار نمی‌گیرد.
const URI = /\b(?:vless|vmess|trojan|ss|hysteria2):\/\/[^\s"'<>\\`]+/gi;
const json = (status, obj, cors) => new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", ...cors } });

async function sha(text) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(b)].slice(0, 8).map(x => x.toString(16).padStart(2, "0")).join("");
}

export default {
  async fetch(req, env) {
    const allowed = env.ALLOWED_ORIGIN || "https://imatixofficel.github.io";
    const cors = { "Access-Control-Allow-Origin": allowed, "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Vary": "Origin" };
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (req.method !== "POST") return json(405, { ok: false, error: "method" }, cors);
    if (req.headers.get("Origin") !== allowed) return json(403, { ok: false, error: "origin" }, cors);

    const raw = await req.text();
    if (raw.length > 8000) return json(413, { ok: false, error: "too_large" }, cors);
    let body; try { body = JSON.parse(raw); } catch { return json(400, { ok: false, error: "json" }, cors); }

    const found = [...new Set(((Array.isArray(body.configs) ? body.configs.join("\n") : "").match(URI) || []))].slice(0, 3);
    if (!found.length) return json(400, { ok: false, error: "no_config" }, cors);
    const ad = String(body.ad || "").replace(/[\u0000-\u001f<>]/g, " ").replace(/\s+/g, " ").trim().slice(0, 200);

    const ip = req.headers.get("CF-Connecting-IP") || "0";
    const user = await sha(ip + (env.SALT || "xfinder"));
    if (env.RL) {                                   // اختیاری: KV برای سقف ۳ اهدا در ساعت برای هر IP
      const k = "rl:" + user, n = parseInt((await env.RL.get(k)) || "0", 10);
      if (n >= 3) return json(429, { ok: false, error: "rate" }, cors);
      await env.RL.put(k, String(n + 1), { expirationTtl: 3600 });
    }

    const r = await fetch(`https://api.github.com/repos/${env.GH_REPO || "imatixofficel/Xfinder"}/dispatches`, {
      method: "POST",
      headers: { Authorization: `Bearer ${env.GITHUB_TOKEN}`, Accept: "application/vnd.github+json", "User-Agent": "xfinder-donate-worker", "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json" },
      body: JSON.stringify({ event_type: "donation", client_payload: { configs: found, ad, user } }),
    });
    if (r.status !== 204) return json(502, { ok: false, error: "github_" + r.status }, cors);
    return json(200, { ok: true }, cors);
  },
};
