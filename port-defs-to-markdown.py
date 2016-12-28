#!/usr/bin/env python3

DESCRIPTION = 'Parse ev3dev *_port_defs.c files and convert to markdown ' \
              'for online documentation.'

import argparse
import glob
import json
import os.path
import re
import subprocess
import sys

def error(message):
    print("Error: {0}".format(message), file=sys.stderr)
    exit(1)

def parse_structured_comment(lines, i, result):
    found = False
    if re.match('\s*/\*\*', lines[i]):
        found = True
        i += 1
        while not re.match('\s*\*/', lines[i]):
            match = re.match('\s*\*\s*@(\w+):\s*(.*)', lines[i])
            if match:
                result[match.group(1)] = match.group(2)
            else:
                match = re.match('\s*\*\s?(.*)', lines[i])
                if match:
                    if not 'notes' in result:
                        result['notes'] = ''
                    if match.group(1).startswith('[^'):
                        result['notes'] += '\n'
                    result['notes'] += match.group(1) + '\n    '
            i += 1
        i += 1
    return found, i

def parse_port(lines, i):
    result = {}
    # first line of a port def should look like "[<index>] = {"
    match = re.match('\s*\[(\w+)\]\s*=\s*\{', lines[i])
    if not match:
        raise Exception('Missing port id assignment at line {0}'.format(i))
    i += 1
    mode_name = match.group(1)
    result[mode_name] = {}
    # parse the lines until we find a closing bracket
    while not re.match('\s*\},?', lines[i]):
        found, i = parse_structured_comment(lines, i, result[mode_name])
        if found:
            continue
        # ignore regular comments "/* ... */"
        if re.match('\s*/\*', lines[i]):
            while not re.match('.*\*/', lines[i]):
                i += 1
            i += 1
            continue
        match = re.match('\s*\.([\w\.]+)\s*=\s*(".*?"|\'.*?\'|-?\d+|\w+|\{),?', lines[i])
        if not match:
            raise Exception('missing closing "}}" at line {0}'.format(i))
        i += 1
        result[mode_name][match.group(1)] = match.group(2).strip('"')
        # opening bracket means we have a array definition. Array defs are
        # structured the same as port defs, so we just call this function
        # recursively
        if match.group(2) == '{':
            result[mode_name][match.group(1)] = []
            while not re.match('\s*\},?', lines[i]):
                port, i = parse_port(lines, i)
                for key in port:
                    port[key]['id'] = key
                    result[mode_name][match.group(1)].append(port[key])
            i += 1
    i += 1
    return result, i

def parse_file(kdir, file_name):
    with open(file_name) as file:
        lines = file.read().split('\n')
    mode_list = []
    port = {}
    i = 0
    # search for the port definitions. Looks like:
    #    const struct <some_type> <some_name>_mode_info[] = {
    while i < len(lines):
        match = re.match('(?:\w+\s)+(\w+)_mode_info\[\w*\]\s=\s\{', lines[i])
        i += 1
        source_line = i
        if match:
            port['name'] = match.group(1).replace('_', '-')
            port['url_name'] = port['name']
            while not re.match('\s*\};', lines[i]):
                try:
                    found, i = parse_structured_comment(lines, i, port)
                    if found:
                        continue
                    mode, i = parse_port(lines, i)
                    for key in mode:
                        mode[key]['id'] = key
                        mode_list.append(mode[key])
                except Exception as ex:
                    error(str(ex) + ' in file  "{0}"'.format(file_name))
            port['mode_info'] = mode_list
            port['num_modes'] = len(mode_list)
            if not 'module' in port:
                port['module'] = file_name.split('/')[-1].replace('_', '-').replace('.c', '')
            port['source_file'] = file_name.replace(kdir, '')
            if port['source_file'][0] == '/':
                port['source_file'] = port['source_file'][1:]
            port['source_line'] = source_line
    if not len(mode_list):
        error("did not find *_mode_info struct in {0}".format(file_name))
    return [ port ]

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('kdir', type=str, help='kernel source directory')
    parser.add_argument('destination', type=str, help='destination folder')
    parser.add_argument('file_names', metavar='file', type=str, nargs='+',
            help='port definition file names')
    args = parser.parse_args()
    proc = subprocess.Popen(['make', '-s', '-C', args.kdir, 'kernelversion'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    kernel_version, err = proc.communicate()
    kernel_version = kernel_version.decode('ascii').strip()
    if err:
        error(err)
    all_file_names = []
    for arg_file_name in args.file_names:
        file_name = os.path.join(args.kdir, arg_file_name)
        if not os.path.isfile(file_name):
            error('File {0} does not exist.'.format(file_name))
        all_file_names.append(file_name)
    port_list = []
    for file_name in all_file_names:
        port_list += parse_file(args.kdir, file_name)
    port_list.sort(key=lambda port: port['name'])
    with open(args.destination + '/_data/ports.json', 'w') as out_file:
        print(json.dumps(port_list, sort_keys=True, indent=4), file=out_file)
    for idx, item in enumerate(port_list):
        dest_file = '{0}/docs/ports/{1}.markdown'.format(args.destination, item['url_name'])
        with open(dest_file, 'w') as out_file:
            print('---', file=out_file)
            print('autogen:', 'This file was automatically generated by ' +
                    'ports-defs-to-markdown.py', file=out_file)
            print('kernel_version:', kernel_version, file=out_file)
            print('source_file:', item['source_file'], file=out_file)
            print('source_line:', item['source_line'], file=out_file)
            print('title:', item['description'], file=out_file)
            print('port_index:', idx, file=out_file)
            print('---', file=out_file)
            print('', file=out_file)
            print('{% include /docs/port.md %}', file=out_file)

if __name__ == '__main__':
    main()
