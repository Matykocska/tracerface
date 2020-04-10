from pathlib import Path
from subprocess import CalledProcessError, check_output
import yaml


class Setup:
    def __init__(self):
        self._setup = {}

    # initialize app and its functions for tracing
    def initialize_app(self, path):
        try:
            symbols = check_output(['nm', path]).decode().rstrip().split('\n')
        except CalledProcessError:
            raise ValueError('Could not find binary at {}'.format(path))
        functions = [symbol.split()[-1] for symbol in symbols]
        init_state = {}
        for function in functions:
            init_state[function] = {
                'traced': False,
                'parameters': {}
            }
        self._setup[path] = init_state

    # Remove application from getting traced
    def remove_app(self, app):
        del self._setup[app]

    # Returns apps currently saved
    def get_apps(self):
        return list(self._setup.keys())

    # Return functions and their state of a given application
    def get_setup_of_app(self, app):
        return self._setup[app]

    # Sets up a function to be traced
    def add_function(self, app, function):
        try:
            self._setup[app][function]['traced'] = True
        except KeyError:
            raise ValueError('No function named {} was found in {}'.format(function, app))

    # Removes a function from traced ones
    def remove_function(self, app, function):
        self._setup[app][function]['traced'] = False

    # Returns the indexes where a parameter is set for tracing
    def get_parameters(self, app, function):
        return self._setup[app][function]['parameters']

    # Sets up a parameter to be traced
    def add_parameter(self, app, function, index, format):
        self._setup[app][function]['parameters'][index] = format

    # Removes a parameter from traced ones
    def remove_parameter(self, app, function, index):
        del self._setup[app][function]['parameters'][index]

    # Convert dictionary of functions to trace into properly
    # structured list of args to be used by the trace tool
    def generate_bcc_args(self):
        arguments = []
        for app in self._setup:
            for function in self._setup[app]:
                if self._setup[app][function]['traced']:
                    argument = '{}:{}'.format(app, function)
                    params = self._setup[app][function]['parameters']
                    if params:
                        argument = '{} "{}", {}'.format(
                            argument,
                            ' '.join([params[index] for index in params]),
                            ', '.join(['arg{}'.format(index) for index in params]))
                    arguments.append(argument)
        return arguments

    def load_from_file(self, path):
        try:
            content = Path(path).read_text()
        except FileNotFoundError:
            raise ValueError('Could not find config file at {}'.format(path))
        except IsADirectoryError:
            raise ValueError('{} is a directory, not a file'.format(path))

        try:
            config = yaml.safe_load(content)
        except yaml.parser.ParserError:
            raise ValueError('File format is incorrect')

        try:
            for app in config:
                self.initialize_app(app)
                for function in config[app]:
                    self.add_function(app, function)
                    for index in config[app][function]:
                        self.add_parameter(app, function, index, config[app][function][index])
        except TypeError:
            raise ValueError('File format is incorrect')
