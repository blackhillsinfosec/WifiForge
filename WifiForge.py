#!/usr/bin/env python3

from blessed import Terminal
from subprocess import DEVNULL
import os
import importlib.util
import inspect
import sys
import textwrap
from mn_wifi.mobility import Mobility, ConfigMobLinks
from mn_wifi.module import Mac80211Hwsim

def print_banner():
    print("  ")

ascii_art = """
                                  ██████████                                  
                             ████████████████████                             
                          ██████████████████████████                          
                       ████████████████████████████████                       
                     ███████████████████████████████████                      
                    █████████████████████████████████████                     
                    00 ███████                 ███████ 00                     
                    11 0 ██    ███████████████    ██ 0 11                     
                    00 1  0 █████████████████████ 0  1 00                     
                    11 0  1 █████████████████████ 1  0 11                     
                    00 1  0 0 ██████     ██████ 0 0  1 00                     
             11 0      1 0 1  \u001b[31m███\u001b[0m  1 0 1      0 11      
                1      0 1 0 \u001b[31m█████\u001b[0m 0 1 0      1         
                0      1 0   \u001b[31m1███1\u001b[0m   0 1      0         
                       1   \u001b[31m0 1 0\u001b[0m   1                
                            \u001b[31m1 0 1\u001b[0m                    
                            \u001b[31m0 1 0\u001b[0m                    
                            \u001b[31m1 0 1\u001b[0m                    
                                \u001b[31m1\u001b[0m                        
                                                                              
    ██╗       ██╗██╗███████╗██╗  ███████╗ █████╗ ██████╗  ██████╗ ███████╗    
    ██║  ██╗  ██║██║██╔════╝██║  ██╔════╝██╔══██╗██╔══██╗██╔════╝ ██╔════╝    
    ╚██╗████╗██╔╝██║█████╗  ██║  █████╗  ██║  ██║██████╔╝██║  ██╗ █████╗      
     ████╔═████║ ██║██╔══╝  ██║  ██╔══╝  ██║  ██║██╔══██╗██║  ╚██╗██╔══╝      
      ██╔╝ ╚██╔╝ ██║██║     ██║  ██║     ╚█████╔╝██║  ██║╚██████╔╝███████╗    
      ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝      ╚════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝    
            \u001b[31mBy BHIS\u001b[0m                                                                   
"""

def remove_old_variables():
    ConfigMobLinks.aps = []
    Mac80211Hwsim.hwsim_ids = []
    os.system("mn -c > /dev/null 2>&1")

def import_module_and_get_function(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Get the first non-helper function as before
    functions = {name: func for name, func in inspect.getmembers(module, inspect.isfunction)
                 if name not in ('print_banner', 'CONFIG_TMUX', 'INIT_NET')}
    func_name, function = next(iter(functions.items()), (None, None))
    
    # Try to retrieve the module-level variable 'description'
    description = getattr(module, 'description', "No description provided.")

    return func_name, function, description

def load_functions_from_py_files(directory):
    function_dict = {}
    current_script = os.path.basename(__file__)
    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith(".") and filename != current_script:
            module_name = filename[:-3]
            file_path = os.path.join(directory, filename)
            func_name, function, description = import_module_and_get_function(file_path, module_name)
            if func_name and function:
                # Map filename to a tuple including the function and its description
                function_dict[filename] = (func_name, function, description)
    return function_dict

directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "framework", "labs")
functions = load_functions_from_py_files(directory)
file_names = list(functions.keys())
menu = [file.replace("_", " ").title()[:-3] for file in file_names]

def print_menu(term, selected_index):
    with term.hidden_cursor():
        print(term.clear)
        h, w = term.height, term.width

        # Print ASCII banner
        banner_lines = ascii_art.splitlines()
        banner_height = len(banner_lines)
        for i, line in enumerate(banner_lines):
            print(term.move(i, w // 2 - len(line) // 2) + line)

        # Layout values for the menu and description boxes
        top_offset = banner_height + 2
        menu_height = len(menu) + 2  # for border
        lab_column_width = max(len(name) for name in menu) + 4
        
        # Here we take the description from the currently selected lab file.
        # We also wrap it in case it's too long.
        current_file = file_names[selected_index]
        lab_description = functions[current_file][2]
        # Use a minimum width or adjust as needed
        desc_width = max(40, lab_column_width + 10)
        wrapped = textwrap.wrap(lab_description, width=desc_width - 2)
        spacing_between = 4

        inner_width = lab_column_width + desc_width + spacing_between
        outer_width = inner_width + 2
        outer_height = menu_height + 2

        outer_left = max((w - outer_width) // 2, 0)
        outer_top = top_offset

        lab_left = outer_left + 1
        desc_left = lab_left + lab_column_width + spacing_between

        # Draw outer box
        print(term.move(outer_top, outer_left) + "┌" + "─" * (outer_width - 2) + "─┐")
        print(term.move(outer_top, outer_left) + "" + "┌|Version 3.4.0|" + "" * (outer_width - 2) + "")
        for i in range(outer_height - 2):
            print(term.move(outer_top + 1 + i, outer_left) + "│" + " " * (outer_width - 2) + " │")
        print(term.move(outer_top + outer_height - 1, outer_left) + "└" + "─" * (outer_width - 2) + "─┘")

        # ── Draw lab box ──
        lab_label = " Labs "
        label_pos = (lab_column_width - 2 - len(lab_label)) // 2
        lab_top_border = " ┌" + "─" * label_pos + lab_label + "─" * (lab_column_width - 2 - label_pos - len(lab_label)) + "┐"
        print(term.move(outer_top + 1, lab_left) + lab_top_border)

        for idx in range(menu_height - 2):
            line = menu[idx].ljust(lab_column_width - 2)
            if idx == selected_index:
                line = term.red(line)
            print(term.move(outer_top + 2 + idx, lab_left) + " │" + line + "│")

        print(term.move(outer_top + menu_height, lab_left) + " └" + "─" * (lab_column_width - 2) + "┘")

        # ── Draw description box ──
        desc_label = " Description "
        desc_label_pos = (desc_width - 2 - len(desc_label)) // 2
        desc_top_border = (
            "┌" + "─" * desc_label_pos + desc_label + "─" * (desc_width - 2 - desc_label_pos - len(desc_label)) + "┐"
        )
        print(term.move(outer_top + 1, desc_left) + desc_top_border)

        # Print the wrapped description text in the box
        for i in range(menu_height - 2):
            content = wrapped[i] if i < len(wrapped) else ""
            print(term.move(outer_top + 2 + i, desc_left) + "│" + content.ljust(desc_width - 2) + "│")

        print(term.move(outer_top + menu_height, desc_left) + "└" + "─" * (desc_width - 2) + "┘")

def main():
    term = Terminal()
    current_row = 0
    with term.cbreak(), term.fullscreen():
        while True:
            print_menu(term, current_row)
            key = term.inkey()

            if key.code == term.KEY_UP and current_row > 0:
                current_row -= 1
            elif key.code == term.KEY_DOWN and current_row < len(menu) - 1:
                current_row += 1
            elif key.code in (term.KEY_ENTER, '\n', '\r'):
                os.system("clear")
                # Optionally redirect output during function execution
                sys.stdout = open(os.devnull, 'w')
                functions[file_names[current_row]][1]()  # execute lab function
                remove_old_variables()
                sys.stdout = sys.__stdout__
            elif key.lower() == 'q':
                return

if __name__ == "__main__":
    if os.geteuid() == 0:
        os.system("clear")
        main()
        os.system("clear")
    else:
        print("WIFIFORGE must be run as root!")
        exit(0)
