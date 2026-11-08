import time
import traceback
from datetime import datetime
from functools import wraps


def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        RESET = "\033[0m"

        CHECK_MARK = "\u2705"
        CROSS_MARK = "\u274c"

        BLUE = "\033[94m"
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"

        start_time = time.time()
        timestamp_start = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(
            f"{YELLOW}[{timestamp_start}]{RESET}"
            + f" {BLUE}Commencing Test ({func.__module__})\n"
            + f"Running test function{RESET}"
            + f" {func.__name__}"
        )

        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            traceback.print_exc()
            tb = e.__traceback__
            error = str(e)

        end_time = time.time()
        timestamp_end = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        duration = end_time - start_time

        if success:
            status = f"{GREEN}{CHECK_MARK} Success{RESET}"
            tb = ""
        else:
            status = f"{RED}{CROSS_MARK} Failure: {error}{RESET}"

        print(
            f"{YELLOW}[{timestamp_end}]{RESET}"
            + f"{BLUE} Ran function in {duration:.4f} seconds{RESET} - "
            + f"{status}\n"
            + f"Stack trace info:\n{tb}\n"
            if tb
            else "" + "--------------------------------------------------------------------\n"
        )

        return result

    return wrapper
