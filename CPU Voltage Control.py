# version 1.5.0 (03.10.2023)
VERSION = 'v1.5.0 (03.10.2023)'

from subprocess import check_output, PIPE
from os import system, listdir
from os.path import isdir
from time import sleep

class Shared:
    VOLTAGE_OFFSETS_LABELS = {
        'EEM_DET_L': 'Little Cores',
        'EEM_DET_B': 'Big Cores',
        'EEM_DET_CCI': 'CPU Bus',
        'EEM_DET_GPU': 'GPU'
    }
    voltage_offsets = {}
    vomin = -50
    vomax = 50
    vonew = 0
    current_choosed_offset = None

    def call(proc):
        try:
            out = check_output(['su', '-c']+proc, stderr=PIPE)
            return out.decode('cp1251').strip()
        except Exception as E:
            return None

    def clear_console():
        system('clear')
    
    def is_rooted():
        if Shared.call(['ls', '/data']) is None:
            return False
        return True
    
    def init_voltage_offsets():
        for obj in listdir('/proc/eem/'):
            eem_path = '/proc/eem/'+obj
            if isdir(eem_path):
                eem_offset_path = eem_path+'/eem_offset'
                if not isdir(eem_offset_path):
                    name = Shared.VOLTAGE_OFFSETS_LABELS.get(obj, obj)
                    Shared.voltage_offsets[name] = VoltageOffset(name, eem_offset_path)
    
class VoltageOffset:
    def __init__(self, offset_name: str, offset_path: str):
        self.name = offset_name
        self.path = offset_path

class VoltageControl:
    def set_voltage_offset():
        if Shared.vonew < Shared.vomin or Shared.vonew > Shared.vomax:
            return False
        result = Shared.call(['echo', '"{}"'.format(Shared.vonew), '>', Shared.current_choosed_offset.path])
        if result is None:
            return False
        return True

    def print_voltage_offsets():
        for voltage_offset_name, voltage_offset in Shared.voltage_offsets.items():
            print('[*] Current voltage offset for {0}: {1}'.format(voltage_offset_name, Shared.call(['cat', voltage_offset.path])))
        input('\nPress Enter to continue...')

    def input_voltage_offset():
        try:
            print('[*] Current voltage offset for {0}: {1}'.format(Shared.current_choosed_offset.name, Shared.call(['cat', Shared.current_choosed_offset.path])))
            voltage_offset = int(input('Input new voltage offset [{0} - {1}]: '.format(Shared.vomin, Shared.vomax)).strip())
            Shared.vonew = voltage_offset
            return True
        except ValueError:
            print('[-] Voltage offset isn\'t number!')
            return False
    
    def input_and_set_voltage_offset():
        while True:
            if VoltageControl.input_voltage_offset():
                if not VoltageControl.set_voltage_offset():
                    print('[-] Voltage offset should be from {0} to {1}!'.format(Shared.vomin, Shared.vomax))
                else: # OK
                    break
            print()
            
    def reset_voltage_offsets():
        Shared.vonew = 0
        for voltage_offset_name, voltage_offset in Shared.voltage_offsets.items():
            Shared.current_choosed_offset = voltage_offset
            VoltageControl.set_voltage_offset()

class MenuAction:
    def __init__(self, name):
        self.__name = name
        self.__menu = None
        self.__command = None

    def connect_menu(self, menu):
        if self.__command is not None:
            raise RuntimeError('Command is already connected!')
        self.__menu = menu
    
    def connect_command(self, command):
        if self.__menu is not None:
            raise RuntimeError('Menu is already connected!')
        self.__command = command
    
    def name(self):
        return self.__name
    
    def run(self):
        if self.__menu is not None:
            print(type(self.__menu))
            self.__menu.view()
        elif self.__command is not None:
            self.__command()
        else:
            raise RuntimeError('This action is not connected to a Menu or Command!')

class Menu(object):
    def __init__(self, title: str):
        self.title = title
        self.actions = {}
        self.argvs = {}

    def add_action(self, name: str, menu=None, command=None):
        action = MenuAction(name)
        if command is not None:
            action.connect_command(command)
        elif menu is not None:
            action.connect_menu(menu)
        self.actions[len(self.actions)+1] = action

    def setup(self):
        pass

    def overload_setup(self, custom_setup_function):
        self.setup = custom_setup_function

    def view(self):
        self.setup()
        while True:
            Shared.clear_console()
            print(self.title)
            for index, action in self.actions.items():
                print('    {0} - {1}'.format(index, action.name()))
            try:
                index = int(input('>>> ').strip())
                if index not in self.actions:
                    continue
                print()
            except ValueError:
                continue
            if self.actions[index].name() in Shared.voltage_offsets:
                Shared.current_choosed_offset = Shared.voltage_offsets[self.actions[index].name()]
            self.actions[index].run()

if __name__ == '__main__':
    if not Shared.is_rooted():
        print('[-] Not granted root rights!!!') 
        exit(-1)

    Shared.init_voltage_offsets()                 
    if Shared.voltage_offsets == []:
        print('[-] Your CPU or OC is not supported!!!')
        exit(-2)

    main_menu = Menu('CPU Voltage Control {0} by rzc0d3r'.format(VERSION))

    undervoltage_menu = Menu('CPU Voltage Control {0} by rzc0d3r [UnderVoltage]'.format(VERSION))

    def undervoltage_menu_custom_setup():
        Shared.vomin = -50
        Shared.vomax = 0

    undervoltage_menu.overload_setup(undervoltage_menu_custom_setup)
    for voltage_offset_name in Shared.voltage_offsets:
        undervoltage_menu.add_action(voltage_offset_name, command=VoltageControl.input_and_set_voltage_offset)
    undervoltage_menu.add_action('Back', menu=main_menu)
    undervoltage_menu.add_action('Exit', command=exit)

    overvoltage_menu = Menu('CPU Voltage Control {0} by rzc0d3r [OverVoltage]'.format(VERSION))
    
    def overvoltage_menu_custom_setup():
        Shared.vomin = 0
        Shared.vomax = 50

    overvoltage_menu.overload_setup(overvoltage_menu_custom_setup)
    for voltage_offset_name in Shared.voltage_offsets:
        overvoltage_menu.add_action(voltage_offset_name, command=VoltageControl.input_and_set_voltage_offset)
    overvoltage_menu.add_action('Back', menu=main_menu)
    overvoltage_menu.add_action('Exit', command=exit)

    main_menu.add_action('UnderVoltage', menu=undervoltage_menu)
    main_menu.add_action('OverVoltage', menu=overvoltage_menu)
    main_menu.add_action('View Current Offsets', command=VoltageControl.print_voltage_offsets)
    main_menu.add_action('Reset Offsets', command=VoltageControl.reset_voltage_offsets)
    main_menu.add_action('Exit', command=exit)

    main_menu.view()