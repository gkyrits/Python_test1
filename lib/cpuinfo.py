
def get_cpuUsage():
    try:
        import psutil
    except:
        return ''    
    return psutil.cpu_percent(interval=2)

def get_cpuTemp():
    try:
        import gpiozero as gpio
    except:
        return ''
    return int(gpio.CPUTemperature().value*100)

def get_memUsage():
    # used memory in %, counted as (total - available) / total
    try:
        import psutil
        return psutil.virtual_memory().percent
    except:
        pass
    # no psutil: read /proc/meminfo (any Linux, Raspberry Pi OS included)
    try:
        mem = {}
        with open('/proc/meminfo') as f:
            for line in f:
                key, val = line.split(':', 1)
                mem[key] = int(val.split()[0])  # value in kB
        total = mem['MemTotal']
        avail = mem['MemAvailable']
    except:
        return ''
    return round((total - avail) * 100 / total, 1)



if __name__ == '__main__':
    print('CPU usage : {}%'.format(get_cpuUsage()))
    print('CPU temper: {}'.format(get_cpuTemp()))
    print('Mem usage : {}%'.format(get_memUsage()))