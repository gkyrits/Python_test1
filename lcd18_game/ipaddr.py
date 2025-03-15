import socket
import struct

NO_IPADDR='--.--.--.--'

def get_ip_address(ifname):
    try:
        import fcntl
    except:
        ip=NO_IPADDR
        return ip    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ip= socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(ifname[:15],'utf-8')) 
            )[20:24])
    except:        
        ip=NO_IPADDR
    s.close()
    return ip

if __name__ == '__main__':
    print('eth0:'+get_ip_address('eth0'))
    print('wlan0:'+get_ip_address('wlan0'))