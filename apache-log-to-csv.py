#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function  # Only needed for Python 2

"""
Small tool to convert Apache log files to csv.
Written by Paul Biester (http://isonet.fr)
This package is © 2014 Paul Biester, released under the terms of the GNU GPL v3 (or at your option a later version)

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__author__ = "Paul Biester"
__copyright__ = "Copyright 2014, Paul Biester"
__credits__ = [""]
__license__ = "GPLv3"
__version__ = "1.0"
__maintainer__ = "Paul Biester"
__email__ = "p.biester@isonet.fr"
__status__ = "Beta"

import csv, sys
import apache_log_parser
import argparse


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def main(**kwargs):

    line_parser = apache_log_parser.make_parser(kwargs['format'])
    header = True
    columns_arg = kwargs['columns']
    input_arg = kwargs['input']
    output_arg = kwargs['output']
    derived_names = []
    derived_blocks = []
    derived_arg = kwargs['derivedcolumns']
    if derived_arg:
        derived_arg_split = derived_arg.split('|')
        derived_names = derived_arg_split[0::2]
        derived_blocks = derived_arg_split[1::2]
        # TODO more validation of input here

    progressFile = sys.stdout

    if input_arg == '-':
        inFile = sys.stdin
    else:
        inFile = open(input_arg, 'rb')

    if output_arg == '-':
        outFile = sys.stdout
        progressFile = sys.stderr
    else:
        outFile = open(output_arg, 'w')

    print('Converting, please wait...', file=progressFile)

    lines = inFile.readlines()
    writer = csv.writer(outFile, delimiter='\t')

    for line in lines:
        try:
            log_line_data = line_parser(line)
        except apache_log_parser.LineDoesntMatchException as ex:
            print(Colors.FAIL + 'The format specified does not match the log file. Aborting...' + Colors.ENDC, file=progressFile)
            print('Line: ' + ex.log_line + 'RegEx: ' + ex.regex, file=progressFile)
            exit()

        if header:
            if columns_arg == 'ALL':
                columns = list(log_line_data.keys())
            else:
                columns = columns_arg.split(',')
            writer.writerow(columns + derived_names)
            header = False
        else:
            values = []
            for column in columns:
                values.append(log_line_data[column])

            for derivedBlock in derived_blocks:
                values.append(eval(derivedBlock))
            writer.writerow(values)

    print(Colors.OKGREEN + 'Conversion finished.' + Colors.ENDC, file=progressFile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Apache logs to csv', version='%(prog)s 1.0')
    parser.add_argument('--format', '-f', type=str, help='Apache log format (see http://httpd.apache.org/docs/2.2/logs.html)')
    parser.add_argument('--input', '-i', type=str, help='Input log file ex. /var/log/apache/access.log', default='-')
    parser.add_argument('--output', '-o', type=str, help='Output csv file ex. ~/accesslog.csv', default='-')
    parser.add_argument('--columns', '-c', type=str, help='Output columns, comma delimited, ex. status,time_received_utc_isoformat,request_url_query', default='ALL')
    parser.add_argument('--derivedcolumns', '-d', type=str, help='Additional derived/calculated columns using python syntax, pipe delimited, ex. colname|log_line_data["request_url"].split("/")[-1]', default='')
    args = parser.parse_args()
    main(**vars(args))
