import time

class Logger:
    def log(message):
        print(f"[!] {time.strftime('%Y-%m-%d %H:%M:%S')} -- {message}")

    def error(message):
        print(f"[x] {time.strftime('%Y-%m-%d %H:%M:%S')} -- {message}")