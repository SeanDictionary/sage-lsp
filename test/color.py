# ANSI color codes
class Color:
    BLUE = '\033[34m'      # Client sends
    GREEN = '\033[32m'     # Client receives / Success
    YELLOW = '\033[33m'    # Warnings
    RED = '\033[31m'       # Errors
    BOLD = '\033[1m'       # Bold text
    RESET = '\033[0m'      # Reset color

    @staticmethod
    def blue(text: str) -> str:
        return f"{Color.BLUE}{text}{Color.RESET}"
    
    @staticmethod
    def green(text: str) -> str:
        return f"{Color.GREEN}{text}{Color.RESET}"
    
    @staticmethod
    def yellow(text: str) -> str:
        return f"{Color.YELLOW}{text}{Color.RESET}"
    
    @staticmethod
    def red(text: str) -> str:
        return f"{Color.RED}{text}{Color.RESET}"
    
    @staticmethod
    def bold(text: str) -> str:
        return f"{Color.BOLD}{text}{Color.RESET}"