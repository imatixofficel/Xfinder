"""Minimal stand-in for Xray used ONLY by offline tests.
  version                 -> prints version
  run -test -config F     -> exit 23 if any outbound is unsupported (like real xray would)
  run -c F                -> SOCKS5 inbounds; an outbound whose id/password starts with
                             'good' answers HTTP probes, anything else drops the connection.
"""
import asyncio, json, sys

BAD_PROTOCOLS = {"hysteria2"}


def load(args):
    for flag in ("-config", "-c"):
        if flag in args:
            return json.load(open(args[args.index(flag) + 1]))
    sys.exit(2)


def cred(out):
    s = out.get("settings", {})
    if "vnext" in s:
        return s["vnext"][0]["users"][0].get("id", "")
    if "servers" in s:
        return s["servers"][0].get("password", "")
    return ""


def check(cfg):
    for o in cfg["outbounds"]:
        if o["protocol"] in BAD_PROTOCOLS or o.get("streamSettings", {}).get("network") not in (None, "tcp", "ws", "grpc", "http"):
            print("unknown protocol", o["protocol"], file=sys.stderr)
            sys.exit(23)


async def serve(cfg):
    rules = {r["inboundTag"][0]: r["outboundTag"] for r in cfg["routing"]["rules"]}
    outs = {o["tag"]: o for o in cfg["outbounds"]}

    def handler_for(out):
        good = cred(out).startswith("good")

        async def h(r, w):
            try:
                await r.readexactly(2)
                n = (await r.read(1))  # nmethods consumed loosely
                await r.read(255)
                w.write(b"\x05\x00")
                await w.drain()
                req = await r.readexactly(4)
                if req[3] == 3:
                    ln = (await r.readexactly(1))[0]
                    await r.readexactly(ln + 2)
                elif req[3] == 1:
                    await r.readexactly(6)
                else:
                    await r.readexactly(18)
                if not good:
                    w.close(); return
                w.write(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")
                await w.drain()
                data = await r.read(2048)
                if b"204" in data.split(b"\r\n")[0]:
                    w.write(b"HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n")
                else:
                    body = b"colo=TEST\n"
                    w.write(b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n" % len(body) + body)
                await w.drain()
            except Exception:
                pass
            finally:
                try: w.close()
                except Exception: pass
        return h

    servers = []
    for i in cfg["inbounds"]:
        out = outs[rules[i["tag"]]]
        servers.append(await asyncio.start_server(handler_for(out), "127.0.0.1", i["port"]))
    await asyncio.Event().wait()


def main():
    a = sys.argv[1:]
    if a[:1] == ["version"]:
        print("Xray 0.0-fake"); return
    cfg = load(a)
    check(cfg)
    if "-test" in a:
        return
    asyncio.run(serve(cfg))


main()
