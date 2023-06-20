from subprocess import check_output, PIPE
from os import system

def call(proc):
    try:
        out = check_output(['su', '-c']+proc, stderr=PIPE)
        return out.decode('cp1251').strip()
    except Exception as E:
        return None

def volt_menu(target, vmin, vmax, auto=False):
    cur_off_volt = call(['cat', target])
    try:
        if auto:
            new_off_volt = 0
        else:
            print('[*] Current Offset =', cur_off_volt)
            new_off_volt = int(input(f'Input offset({vmin} - {vmax}): '))
        if new_off_volt <= vmax and new_off_volt >= vmin:
            system(f'su -c "echo {new_off_volt} > {target}"')            
        else:
            print('\n[-] Invalid offset!!!')
    except:
        print('\n[-] Invalid offset!!!')

def volt_offsets(targets):
    for target in targets:
        name, path = target
        cur_off_volt = call(['cat', path])
        print(f'[*] Current Offset for {name}: {cur_off_volt}mV')
    
little = '/proc/eem/EEM_DET_L/eem_offset'
big = '/proc/eem/EEM_DET_B/eem_offset'
cci = '/proc/eem/EEM_DET_CCI/eem_offset'
gpu = '/proc/eem/EEM_DET_GPU/eem_offset'

system('clear')

def menu(name_menu, vmin, vmax):
    while True:
        system('clear')
        print(name_menu)
        print('    1 - Little Cores')
        print('    2 - Big Cores')
        print('    3 - CPU Cache')
        print('    4 - GPU')
        print('    5 - Current Offsets')
        print('    6 - Exit')
        method = input('>>> ').strip()
        print()
        if method == '1':
            volt_menu(little, vmin, vmax)
        elif method == '2':
            volt_menu(big, vmin, vmax)
        elif method == '3':
            volt_menu(cci, vmin, vmax)
        elif method == '4':
            volt_menu(gpu, vmin, vmax)
        elif method == '5':
            volt_offsets([
             	    ('Little Cores', little),
             	    ('Big Cores', big),
             	    ('CPU Cache', cci),
             	    ('GPU', gpu)
            ])
        elif method == '6':
            break
        input('\nPress Enter...')

if call(['ls', '/data']) is None:
    print('[-] Not granted root rights!!!') 
    exit(-1)
                         
if call(['cat', little, big, cci, gpu]) is None:
	print('[-] Your CPU or OC is not supported!!!')
	exit(-2)
	
while True:
    system('clear')
    print('Mediatek Voltage Control v1.3 by rzc0d3r')
    print('    1 - Undervoltage (Safe)')
    print('    2 - Unlock Overvoltage (Warning!!!)')
    print('    3 - Current Offsets')
    print('    4 - Reset Offsets')
    print('    5 - Exit')
    method = input('>>> ').strip()
    if method == '1':
        menu('Mediatek Voltage Control v1.3 [Undervolt]', -50, 0)
    elif method == '2':
        menu('Mediatek Voltage Control v1.3 [OVERVOLT!!!]', 0, 50)
    elif method == '3':
        print()
        volt_offsets([
              ('Little Cores', little),
              ('Big Cores', big),
              ('CPU Cache', cci),
              ('GPU', gpu)
        ])
        input('\nPress Enter...')
    elif method == '4':
        volt_menu(little, 0, 0, True)
        volt_menu(big, 0, 0, True)
        volt_menu(cci, 0, 0, True)
        volt_menu(gpu, 0, 0, True)
        input('\nPress Enter...')
    elif method == '5':
        break