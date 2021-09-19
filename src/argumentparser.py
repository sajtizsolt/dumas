from util import print_exception_and_exit, print_message_and_exit

import os, sys

class ArgumentParser:

  configuration_path = ''
  logging_level = 0

  HELP_MESSAGE = '''
    Usage: python main.py [options] <configuration-file-path>

    where options include:

      --logging-level <level> : This option sets the logging level of the
                                application. The level argument can only have
                                the value of 0, 10, 20, 30, 40 or 50.
  '''

  TOO_FEW_ARGUMENTS_MESSAGE = '''
    Too few command line arguments. You must specify at least the configuration
    file path of the application. Note that this should be the last argument!
  '''

  NO_LOGGING_LEVEL_MESSAGE = '''
    If you use the --logging-level option you should also specify the level of
    logging.
  '''

  LOGGING_LEVEL_NUMERIC_MESSAGE = '''
    The logging level must be a numeric value.
  '''

  INVALID_LOGGING_LEVEL_MESSAGE = '''
    The level argument can only have the value of 0, 10, 20, 30, 40 or 50.
  '''

  INVALID_CONFIGURATION_FILE_PATH = '''
    The specified configuration file path is invalid. Please check if the given
    file exists.
  '''

  @staticmethod
  def show_help():
    print(ArgumentParser.HELP_MESSAGE, file=sys.stderr)

  @staticmethod
  def verify_arguments():
    try:
      argument_count = len(sys.argv)
      if argument_count < 2:
        raise ValueError(ArgumentParser.TOO_FEW_ARGUMENTS_MESSAGE)
      for i in range(argument_count):
        if sys.argv[i] == '--help':
          ArgumentParser.show_help()
          sys.exit()
        elif sys.argv[i] == '--logging-level':
          i += 1
          if not sys.argv[i].isnumeric():
            raise ValueError(ArgumentParser.LOGGING_LEVEL_NUMERIC_MESSAGE)
          if int(sys.argv[i]) not in [0, 10, 20, 30, 40, 50]:
            raise ValueError(ArgumentParser.INVALID_LOGGING_LEVEL_MESSAGE)
          ArgumentParser.logging_level = int(sys.argv[i])
      if not os.path.isfile(sys.argv[argument_count - 1]):
        if sys.argv[argument_count - 1] == ArgumentParser.logging_level:
          raise ValueError(ArgumentParser.TOO_FEW_ARGUMENTS_MESSAGE)
        else:
          raise ValueError(ArgumentParser.INVALID_CONFIGURATION_FILE_PATH)
      ArgumentParser.configuration_path = sys.argv[argument_count - 1]
    except IndexError:
      print_message_and_exit(ArgumentParser.NO_LOGGING_LEVEL_MESSAGE)
    except ValueError:
      print_exception_and_exit()
