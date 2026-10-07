import ipaddress
import socket
import struct

try:
    import fcntl
except ImportError:
    fcntl = None

SIOCGIFADDR = 0x8915
TARGETS = ("1.1.1.1", "8.8.8.8", "10.255.255.255", "192.168.0.1", "192.168.1.1")
WIFI = ("wlan", "swlan", "wifi", "eth", "en", "ap")
VPN = ("tun", "ppp", "wg", "tap", "utun")
MOBILE = ("rmnet", "ccmni", "v4-", "pdp")


def interface_addresses() -> list[tuple[str, str]]:
    if fcntl is None:
        return []
    found = []
    try:
        names = [name for _, name in socket.if_nameindex()]
    except OSError:
        return []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for name in names:
            try:
                packed = fcntl.ioctl(sock.fileno(), SIOCGIFADDR, struct.pack("256s", name[:15].encode()))
                found.append((socket.inet_ntoa(packed[20:24]), name))
            except OSError:
                continue
    return found


def routed_addresses() -> list[tuple[str, str]]:
    found = []
    for target in TARGETS:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                sock.connect((target, 1))
                found.append((sock.getsockname()[0], ""))
            except OSError:
                continue
    return found


def kind_of(iface: str) -> str:
    if iface.startswith(VPN):
        return "vpn"
    if iface.startswith(MOBILE):
        return "mobile"
    if iface.startswith(WIFI):
        return "wifi"
    return "other"


def lan_addresses() -> list[dict]:
    named = interface_addresses()
    names = {ip: iface for ip, iface in named}
    seen, result = set(), []
    for ip, iface in named + routed_addresses():
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if ip in seen or not addr.is_private or addr.is_loopback or addr.is_link_local:
            continue
        seen.add(ip)
        iface = iface or names.get(ip, "")
        result.append({"ip": ip, "iface": iface, "kind": kind_of(iface)})
    order = {"wifi": 0, "other": 1, "mobile": 2, "vpn": 3}
    return sorted(result, key=lambda item: order[item["kind"]])
