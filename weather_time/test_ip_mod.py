import ipaddr as ip

print("test ip")
eth_ip = ip.get_ip_address("eth0")
wan_ip = ip.get_ip_address("wlan0")
print("eth if: "+eth_ip)
print("wan_if: "+wan_ip)