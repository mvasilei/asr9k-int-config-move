#! /usr/bin/env python
import re, sys, signal, subprocess

def signal_handler(sig, frame):
    print('Exiting gracefully Ctrl-C detected...')
    sys.exit(0)

def progress(count, total):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', ''))
    sys.stdout.flush()

def send_command(name, command):
    response = subprocess.Popen(['rcomauto ' + name + ' ' + command],
                                stdout=subprocess.PIPE,
                                shell=True)

    if response.returncode == None:
        return response.communicate()[0]
    else:
        print 'An error occurred', response.returncode

def main():
    if len(sys.argv) != 2:
        print "Usage: ./asr-power-glide.py UKXKS1PE01"
        sys.exit(1)

    host = sys.argv[1]

    try:
        with open('port-map', 'r') as f:
            lines = f.readlines()
    except IOError:
        print 'Could not read file hosts'


    map = []
    for interface in lines:
        old, new = interface.strip().split(',')
        if old != new:
            map.append(interface.strip().split(','))

    try:
        with open('new-configuration', 'w') as nf:
            with open('remove-configuration','w') as rf:

                for interface in range(0, len(map)):
                    progress(interface+1, len(map))
                    response = send_command(host, '"show run formal | i ' + map[interface][0] + '"')

                    config = re.findall(r'.*%s\s.*|.*%s\..*' % (map[interface][0], map[interface][0]), response, re.MULTILINE)
                    if config:
                        for i in range(len(config)):
                            new_config = config[i].replace(map[interface][0],map[interface][1])
                            nf.write(new_config + '\n')

                        for i in range(len(config)):
                            rf.write('no ' + config[i] + '\n')

                print
    except IOError as e:
        print 'Operation failed: %s' % e.strerror

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)  # catch ctrl-c and call handler to terminate the script
    main()
