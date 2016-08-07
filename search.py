import sys
import os
import re
from argparse import ArgumentParser
import terminalsize

# String representation for terminal colors
YELLOW = '\033[1;33m'
NO_COLOR = '\033[0m'


class Search(object):
    """
    Class that searches one or more named input files (standard input
    if no files are specified, or the file name '-' is given) for lines
    containing a match to a regular expression pattern.

    As a design pattern was used OOP in order to store parameters as
    object attributes. To encapsulate differences between output
    formats was considered use of polymorphism but in the end it might
    be inefective to have several classes for different print options.
    """

    def __init__(self, files, pattern, underscore, color, machine):
        # List of tuples, where first item in tuple is start position
        # and second item is end position of found pattern.
        self.indexes = []
        # List of paths to files that may contain pattern
        self.files = files
        # String with searched pattern
        self.pattern = pattern
        # If printing '^' under matching text is on
        self.underscore = underscore
        # If highlighting matching text is on
        self.color = color
        # If generating machine readable output is on
        # Machine format: file_name:no_line:start_pos:matched_text
        # Default format: file_name no_line matched_text
        self.machine = machine

    def add_color(self, string, increment=0):
        """Add terminal color into string on given indexes.

        Args:
            string (str): String that is going to be colored.
            increment (int): Value that is added to indexes.

        Returns:
            str: String colored on given indexes.
        """

        result = string
        for index in self.indexes[::-1]:
            start = index[0] + increment
            end = index[1] + increment
            if end > 0 and start < len(string):
                if start < 0:
                    start = 0
                if end > len(string):
                    end = len(string)
                result = result[:start] + YELLOW + string[start:end] \
                    + NO_COLOR + result[end:]

        return result

    def get_underscore_line(self, string, increment=0):
        """Create string containing spaces on places that don't contain
        matching pattern given by indexes. On places where is matching
        pattern print '^'.

        Args:
            string (str): String that is going to be processed.
            increment (int): Value that is added to indexes.

        Returns:
            str: Created underscore line.
        """

        result = ''
        last = 0 + increment
        for index in self.indexes:
            start = index[0] + increment
            end = index[1] + increment
            if end > 0 and start < len(string):
                if start < 0:
                    start = 0
                if end > len(string):
                    end = len(string)

                try:
                    result += ' ' * len(string[last:start].decode("utf-8"))
                except UnicodeDecodeError:
                    result += ' ' * len(string[last:start])
                try:
                    result += '^' * len(string[start:end].decode("utf-8"))
                except UnicodeDecodeError:
                    result += '^' * len(string[start:end])

                last = end
        return result

    def get_match_indexes(self, string):
        """Find the pattern in the string.

        Args:
            string(str): String that is going to be searched.
        """

        self.indexes = [(m.start(0), m.end(0)) for m in re.finditer(
                self.pattern, string)]

    def print_result(self, file_name, no_line, line):
        """Print result to standard output.

        Args:
            file_name(str): Name of the file containing found pattern.
            no_line(int): Number of row that contains found pattern.
            line(str): Line containing matched text.
        """

        if self.machine:
            delimiter = ':'
        else:
            delimiter = ' '

        result = ''

        result += '%s' % file_name
        if len(result) > 0:
            result += delimiter
        result += '%d' % no_line
        if len(result) > 0:
            result += delimiter
        if self.machine:
            result += str(self.indexes[0][0]) + delimiter

        if self.underscore:
            # Decode is called because of length of special characters like
            # Czech diacritics
            try:
                header_size_d = len(result.decode("utf-8"))
            except UnicodeDecodeError:
                header_size_d = len(result)
            header_size = len(result)

            result += line

            # If underscore is used than the line must be split in order
            # to ensure that each pattern in terminal is underscored.
            n = terminalsize.get_terminal_size()[1]
            result = [result[i:i+n] for i in range(0, len(result), n)]
            for k, i in enumerate(result):
                underscore_line = self.get_underscore_line(
                    result[k],
                    header_size-n*k)
                if self.color:
                    result[k] = self.add_color(result[k], header_size-n*k)
                sys.stdout.write('%s\n' % result[k].strip('\n'))

                if k == 0:
                    underscore_line = ' ' * header_size_d + underscore_line
                sys.stdout.write('%s\n' % underscore_line.strip('\n'))

        else:

            if self.color:
                line = self.add_color(line)
            result += line
            sys.stdout.write('%s\n' % result.strip('\n'))

    def search_file(self, filename):
        """Search a single file or standard input for given pattern.

        Args:
            file_name(str): Name of the file containing found pattern or
                standard input.
        """

        if filename == '(standard input)':
            text = sys.stdin
        else:
            try:
                text = open(filename, 'r')
            except IOError:
                sys.stdout.write('Could not read file: ' + filename)
                sys.exit()

        line = re.sub('[^\s!-~]', '', text.readline())
        lineno = 1
        while line:
            self.get_match_indexes(line)
            if self.indexes:
                self.print_result(filename, lineno, line)
            line = text.readline()
            lineno += 1

        text.close()

    def search_files(self):
        """Search files for given pattern."""

        print(self.files)
        for path in self.files:
            if os.path.isfile(path) or path == '(standard input)':
                self.search_file(path)
            else:
                sys.stdout.write('%s is a directory\n' % path)


def setup_parser():
    """Configuration for command line argument parser object.

    Returns:
        object: Configured ArgumentParser.
    """

    parser = ArgumentParser(add_help=False)
    parser.add_argument('pattern', type=str, help='the pattern to find')
    parser.add_argument('files', metavar='FILES', nargs='*', default=['-'],
                        help='the files(s) to search')
    parser.add_argument('-u', '--underscore', action='store_true',
                        help='prints "^" under the matching text')
    parser.add_argument('-c', '--color', action='store_true',
                        help='highlight matching text')
    parser.add_argument('-m', '--machine', action='store_true',
                        help='generate machine readable output')
    return parser


def get_arguments(args):
    parser = setup_parser()
    return parser.parse_args(args)

if __name__ == '__main__':
    args = get_arguments(sys.argv[1:])
    files = [f if f != '-' else '(standard input)' for f in args.files]

    search = Search(
        files=files,
        pattern=args.pattern,
        underscore=args.underscore,
        color=args.color,
        machine=args.machine)
    search.search_files()
