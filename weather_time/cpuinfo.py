import psutil

def get_cpuUsage():
    return psutil.cpu_percent(interval=2)

def get_cpuTemp():
    try:
        import gpiozero as gpio
    except:
        return ''
    return int(gpio.CPUTemperature().value*100)



if __name__ == '__main__':
    print('CPU usage : {}%'.format(get_cpuUsage()))
    print('CPU temper: {}'.format(get_cpuTemp()))