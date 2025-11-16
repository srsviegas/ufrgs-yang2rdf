import time
import colorama

class Logger:
    def log(message):
        print(f"{colorama.Fore.CYAN}[!] {colorama.Fore.RESET}{colorama.Style.DIM}{time.strftime('%Y-%m-%d %H:%M:%S')}{colorama.Fore.RESET}{colorama.Style.RESET_ALL} -- {message}")

    def error(message):
        print(f"{colorama.Fore.RED}[x] {colorama.Fore.RESET}{colorama.Style.DIM}{time.strftime('%Y-%m-%d %H:%M:%S')}{colorama.Fore.RESET}{colorama.Style.RESET_ALL} -- {message}")