"""Tiny MMDB writer for tests (IPv6 tree with an IPv4 subtree at ::/96, 24-bit records, map/string data)."""
import ipaddress, struct


def _enc(v):
    if isinstance(v, str):
        b = v.encode()
        assert len(b) < 29
        return bytes([(2 << 5) | len(b)]) + b
    if isinstance(v, dict):
        assert len(v) < 29
        return bytes([(7 << 5) | len(v)]) + b"".join(_enc(k) + _enc(x) for k, x in v.items())
    if isinstance(v, int):                       # uint32
        b = v.to_bytes(4, "big")
        return bytes([(6 << 5) | 4]) + b
    raise TypeError(v)


def build(entries):
    """entries: {"1.2.3.0/24": {"country": {...}}}"""
    nodes = [[None, None]]
    data, offsets = b"", {}

    def data_off(rec):
        nonlocal data
        key = repr(rec)
        if key not in offsets:
            offsets[key] = len(data)
            data += _enc(rec)
        return offsets[key]

    pend = []
    for cidr, rec in entries.items():
        net = ipaddress.ip_network(cidr)
        bits = [0] * 96 + [int(b) for b in format(int(net.network_address), "032b")][:net.prefixlen]
        node = 0
        for b in bits[:-1]:
            if nodes[node][b] is None:
                nodes.append([None, None]); nodes[node][b] = len(nodes) - 1
            node = nodes[node][b]
        pend.append((node, bits[-1], rec))
    for node, b, rec in pend:
        nodes[node][b] = ("data", data_off(rec))
    n = len(nodes)

    def val(r):
        if r is None:
            return n
        if isinstance(r, tuple):
            return n + 16 + r[1]
        return r
    tree = b"".join(val(a).to_bytes(3, "big") + val(b).to_bytes(3, "big") for a, b in nodes)
    meta = {"node_count": n, "record_size": 24, "ip_version": 6, "binary_format_major_version": 2}
    # metadata: ints must use uint32/uint16 types; encode with uint32 helper above
    return tree + b"\x00" * 16 + data + b"\xab\xcd\xefMaxMind.com" + _enc(meta)
