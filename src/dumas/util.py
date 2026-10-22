import sys


def print_exception_and_exit() -> None:
    exc = sys.exc_info()[1]
    print_message_and_exit(str(exc) if exc else "An unknown error occurred.")


def print_message_and_exit(message: object) -> None:
    sys.stderr.write(f"\n  Error:\n  {message}\n")
    sys.exit(1)
