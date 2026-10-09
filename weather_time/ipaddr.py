import socket
import struct
import sys
import time
import json
import subprocess

# Windows: physical adapters that are up, by media type, with their IPv4 address
# (Get-NetAdapter -Physical leaves out VMware/Hyper-V/VPN adapters)
WIN_MEDIA = {'eth0': '802.3', 'wlan0': '802.11'}  # ifname -> PhysicalMediaType part
WIN_CACHE_TIME = 30  # sec, PowerShell takes ~1 s, raspi_play asks every 5 s
WIN_PS_CMD = ("@(Get-NetAdapter -Physical | Where-Object Status -eq 'Up' | ForEach-Object {"
              " [pscustomobject]@{media=[string]$_.PhysicalMediaType;"
              " ip=@(Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4"
              " -ErrorAction SilentlyContinue | ForEach-Object IPAddress)} })"
              " | ConvertTo-Json -Compress")
win_cache = {'time': 0, 'adapters': []}

def __win_adapters():
    now = time.monotonic()
    if win_cache['time'] and now - win_cache['time'] < WIN_CACHE_TIME:
        return win_cache['adapters']
    adapters = []
    try:
        out = subprocess.run(['powershell', '-NoProfile', '-Command', WIN_PS_CMD],
                             capture_output=True, text=True, timeout=10,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)).stdout
        data = json.loads(out) if out.strip() else []
        if isinstance(data, dict):  #one adapter, not a list
            data = [data]
        for item in data:
            ips = item.get('ip') or []
            if isinstance(ips, str):
                ips = [ips]
            adapters.append((item.get('media', ''), [ip for ip in ips if not ip.startswith('169.254.')]))
    except Exception as e:
        print('Fail get windows ip:', e)
    win_cache['time'] = now
    win_cache['adapters'] = adapters
    return adapters

# same names as on the Pi: eth0 = wired ethernet, wlan0 = Wi-Fi
def __win_ip_address(ifname):
    media = WIN_MEDIA.get(ifname)
    if media is None:
        return '----'
    for adapter_media, ips in __win_adapters():
        if media in adapter_media and ips:
            return ips[0]
    return '----'

# output of a command, '' if it is missing or fails
def __run(cmd, encoding=None):
    try:
        return subprocess.run(cmd, capture_output=True, timeout=5, encoding=encoding, errors='replace',
                              creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)).stdout or ''
    except Exception:
        return ''

# ssid of the connected Wi-Fi, '' if not connected
def get_wifi_name():
    if sys.platform.startswith('win'):
        #'SSID' is not translated in netsh, the console code page is ('oem')
        for line in __run(['netsh', 'wlan', 'show', 'interfaces'], 'oem').splitlines():
            key, sep, val = line.partition(':')
            if sep and key.strip() == 'SSID':
                return val.strip()
        return ''
    ssid = __run(['iwgetid', '-r']).strip()
    if ssid:
        return ssid
    #NetworkManager (Raspberry Pi OS Bookworm): yes:<ssid> for the active one
    for line in __run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi']).splitlines():
        if line.startswith('yes:'):
            return line[4:].replace(r'\:', ':')  #nmcli escapes ':' in names
    return ''

def get_ip_address(ifname):
    if sys.platform.startswith('win'):
        return __win_ip_address(ifname)
    try:
        import fcntl
    except:
        ip='----'
        return ip    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ip= socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(ifname[:15],'utf-8')) 
            )[20:24])
    except:        
        ip='----'
    s.close()
    return ip

if __name__ == '__main__':
    print('eth0:'+get_ip_address('eth0'))
    print('wlan0:'+get_ip_address('wlan0'))
    print('wifi:'+get_wifi_name())