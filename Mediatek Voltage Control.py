# version 1.4.1 (01.08.2023)
from subprocess import check_output, PIPE
from os import system

def call(proc):
    try:
        out = check_output(['su', '-c']+proc, stderr=PIPE)
        return out.decode('cp1251').strip()
    except Exception as E:
        return None

def volt_menu(target: str, vmin: int, vmax: int, resetOffset=False):
    cur_off_volt = call(['cat', target])
    if resetOffset:
        new_off_volt = 0
    else:
        print('[*] Current Offset =', cur_off_volt)
        try:
            new_off_volt = int(input(f'Input offset({vmin} - {vmax}): '))
        except ValueError: # if the user writes a wrong integer
            new_off_volt = vmax+1 # invalid offset will be displayed
    if new_off_volt <= vmax and new_off_volt >= vmin:
        call(['echo', f'"{new_off_volt}"', '>', target])     
    else:
        print('\n[-] Invalid offset!!!')

def volt_offsets(targets: list):
    for target in targets:
        name, path = target
        cur_off_volt = call(['cat', path])
        print(f'[*] Current Offset for {name}: {cur_off_volt}mV')
    
little = '/proc/eem/EEM_DET_L/eem_offset'
big = '/proc/eem/EEM_DET_B/eem_offset'
cci = '/proc/eem/EEM_DET_CCI/eem_offset'
gpu = '/proc/eem/EEM_DET_GPU/eem_offset'
bl = '/proc/eem/EEM_DET_BL/eem_offset'

available_offsets = [
    ('Little Cores', little),
    ('Big Cores', big),
    ('CPU Cache', cci),
    ('GPU', gpu),
    ('BL', bl)
]
supported_offsets = []

system('clear')

def menu(name_menu: str, supported_offsets: list, vmin: int, vmax: int):
    while True:
        system('clear')
        print(name_menu)
        index_offset = 0
        indexed_supported_offsets = {}
        indexed_other_actions = {}
        for offset in supported_offsets:
            index_offset += 1
            print('   ', index_offset, '-', offset[0])
            indexed_supported_offsets[str(index_offset)] = offset
        indexed_other_actions[str(index_offset+1)] = 'Current Offsets'
        indexed_other_actions[str(index_offset+2)] = 'Exit'
        for index_action in indexed_other_actions:
            print('   ', index_action, '-', indexed_other_actions[index_action])
        index = input('>>> ').strip()
        print()
        if index in indexed_supported_offsets.keys():
            volt_menu(indexed_supported_offsets[index][1], vmin, vmax)
        elif index in indexed_other_actions.keys():
            if indexed_other_actions[index] == 'Current Offsets':
                volt_offsets(supported_offsets)
            elif indexed_other_actions[index] == 'Exit':
                break
        else:
            continue
        input('\nPress Enter...')

if call(['ls', '/data']) is None:
    print('[-] Not granted root rights!!!') 
    exit(-1)

# check supported offsets
for offset in available_offsets:
    if call(['cat', offset[1]]) is not None:
        supported_offsets.append(offset)
        print('[+] Your device supports', offset[0], 'offset')
						                                                                 
if supported_offsets == []:
	print('[-] Your CPU or OC is not supported!!!')
	exit(-2)

input('\nPress Enter to continue...')
		
while True:
    system('clear')
    print('Mediatek Voltage Control v1.4.1 by rzc0d3r')
    print('    1 - Undervoltage (Safe)')
    print('    2 - Unlock Overvoltage (Warning!!!)')
    print('    3 - Current Offsets')
    print('    4 - Reset Offsets')
    print('    5 - Exit')
    index = input('>>> ').strip()
    if index == '1':
        menu('Mediatek Voltage Control v1.4.1 [Undervolt]', supported_offsets, -50, 0)
    elif index == '2':
        menu('Mediatek Voltage Control v1.4.1 [OVERVOLT!!!]', supported_offsets, 0, 50)
    elif index == '3':
        print()
        volt_offsets(supported_offsets)
        input('\nPress Enter...')
    elif index == '4':
        for offset in supported_offsets:
            volt_menu(offset[1], 0, 0, True)
        input('\nPress Enter...')
    elif index == '5':
        break