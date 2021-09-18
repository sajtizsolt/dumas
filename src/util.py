import sys

def print_exception_and_exit():
  print_message_and_exit(sys.exc_info()[1])

def print_message_and_exit(message):
  print('\n  Error:')
  print(message, file=sys.stderr)
  sys.exit()
