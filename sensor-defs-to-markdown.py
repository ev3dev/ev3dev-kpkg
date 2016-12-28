#!/usr/bin/env python3

DESCRIPTION = 'Parse ev3dev *_sensor_defs.c files and convert to markdown ' \
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

def parse_sensor(lines, i, name_constants):
    result = {}
    # first line of a sensor def should look like "[<index>] = {"
    match = re.match('\s*\[(\w+)\]\s*=\s*\{', lines[i])
    if not match:
        raise Exception('Missing sensor id assignment at line {0}'.format(i))
    i += 1
    sensor_name = match.group(1)
    result[sensor_name] = {}
    # parse the lines until we find a closing bracket
    while not re.match('\s*\},?', lines[i]):
        if re.match('\s*/\*\*', lines[i]):
            i += 1
            while not re.match('\s*\*/', lines[i]):
                match = re.match('\s*\*\s*@(\w+):\s*(.*)', lines[i])
                if match:
                    result[sensor_name][match.group(1)] = name_constants.get(match.group(2)) or match.group(2)
                else:
                    match = re.match('\s*\*\s?(.*)', lines[i])
                    if match:
                        if not 'notes' in result[sensor_name]:
                            result[sensor_name]['notes'] = ''
                        if match.group(1).startswith('[^'):
                            result[sensor_name]['notes'] += '\n'
                        result[sensor_name]['notes'] += match.group(1) + '\n    '
                i += 1
            i += 1
            continue
        # ignore regular comments "/* ... */"
        if re.match('\s*/\*', lines[i]):
            while not re.match('.*\*/', lines[i]):
                i += 1
            i += 1
            continue
        match = re.match('\s*\.([\w\.]+)\s*=(?:\s*&?\(.*\))?\s*(".*?"|\'.*?\'|-?\d+|[\w\(\)"]+|\{),?', lines[i])
        if not match:
            raise Exception('missing closing "}}" at line {0}'.format(i))
        i += 1
        result[sensor_name][match.group(1)] = (name_constants.get(match.group(2)) or match.group(2)).strip('"')
        # opening bracket means we have a array definition. Arrays defs are
        # structured the same as sensor defs, so we just call this function
        # recursively
        if match.group(2) == '{':
            result[sensor_name][match.group(1)] = []
            while not re.match('\s*\},?', lines[i]):
                # ignoring ops for now since it is a struct rather than an array
                if match.group(1) == "ops":
                    i += 1;
                    continue
                sensor, i = parse_sensor(lines, i, name_constants)
                for key in sensor:
                    sensor[key]['id'] = key
                    result[sensor_name][match.group(1)].append(sensor[key])
            i += 1
    i += 1
    return result, i

def get_url_name(sensor):
    url_name = sensor['vendor_part_name']
    if 'vendor_name' in sensor:
        url_name = '{0} {1}'.format(sensor['vendor_name'], url_name)
    return re.sub('[^\w\.]+', '-', url_name.lower()).replace('--', '-').strip('-')

def parse_header(file_name, dict):
    """Parse the header file for #defines that have a string value and save the
    result in dict."""
    with open(file_name) as file:
        lines = file.read().split('\n')
    i = 0
    while i < len(lines):
        match = re.match('#define\s+(\w+)\s+"([\w-]+)"', lines[i])
        i += 1
        if match:
            dict[match.group(1)] = match.group(2)

def parse_file(kdir, file_name, name_constants):
    with open(file_name) as file:
        lines = file.read().split('\n')
    sensor_list = []
    i = 0
    # search for the sensor definitions. Looks like:
    #    const struct <some_type> <some_name>_defs[] = {
    while i < len(lines):
        match = re.match('(?:\w+\s)+(\w+)_defs\[\]\s=\s\{', lines[i])
        i += 1
        source_line = i
        if match:
            sensor_type = match.group(1).replace('_', '-')
            while not re.match('\s*\};', lines[i]):
                try:
                    sensor, i = parse_sensor(lines, i, name_constants)
                    for key in sensor:
                        sensor[key]['id'] = key
                        sensor[key]['sensor_type'] = sensor_type
                        sensor[key]['url_name'] = get_url_name(sensor[key])
                        sensor[key]['source_file'] = file_name.replace(kdir, '')
                        if sensor[key]['source_file'][0] == '/':
                            sensor[key]['source_file'] = sensor[key]['source_file'][1:]
                        sensor[key]['source_line'] = source_line
                        sensor_list.append(sensor[key])
                except Exception as ex:
                    error(str(ex) + ' in file  "{0}"'.format(file_name))
    if not len(sensor_list):
        error("did not find *_defs struct in {0}".format(file_name))
    return sensor_list

def get_sensor_sort_key(sensor):
    """Returns vendor_name concatenated with vendor_part_number"""
    key = ""
    key += 'vendor_name' in sensor and sensor['vendor_name'] or ""
    key += 'vendor_part_number' in sensor and sensor['vendor_part_number'] or ""
    return key

def get_sensor_page_title(sensor):
    """Generates a page title out of the vendor information of a sensor"""
    return ('vendor_name' in sensor and '{0} '.format(sensor['vendor_name']) \
            or "") + sensor['vendor_part_name'] + ('vendor_part_number' in \
            sensor and ' ({0})'.format(sensor['vendor_part_number']) or "")

def main():
    # setup command line parameters
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--kernel', type=str, help='kernel source directory')
    parser.add_argument('--website', type=str, help='destination folder')
    parser.add_argument('--header-files', metavar='header', type=str, nargs='+',
            help='header file names')
    parser.add_argument('--source-files', metavar='file', type=str, nargs='+',
            help='sensor definition file names')
    args = parser.parse_args()

    # get the kernel version
    proc = subprocess.Popen(['make', '-s', '-C', args.kernel, 'kernelversion'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    kernel_version, err = proc.communicate()
    kernel_version = kernel_version.decode('ascii').strip()

    # expand list of files in --header-files arg using glob
    all_header_file_names = []
    for arg_file_name in args.header_files:
        arg_file_names = glob.glob(os.path.join(args.kernel, arg_file_name))
        for file_name in arg_file_names:
            if not os.path.isfile(file_name):
                error('File {0} does not exist.'.format(file_name))
            all_header_file_names.append(file_name)

    # expand list of files in --source-files arg using glob
    source_file_names = []
    for arg_file_name in args.source_files:
        arg_file_names = glob.glob(os.path.join(args.kernel, arg_file_name))
        for file_name in arg_file_names:
            if not os.path.isfile(file_name):
                error('File {0} does not exist.'.format(file_name))
            source_file_names.append(file_name)

    # name constants will be used to substitute constant names for real string values
    name_constants = {}

    # special case for EV3 UART sensors
    for type_id in range(0, 128):
        key = 'EV3_UART_SENSOR_NAME("{0}")'.format(type_id)
        value = 'lego-ev3-uart-{0}'.format(type_id)
        name_constants[key] = value

    # parse header files to get all other name constants
    for file_name in all_header_file_names:
        parse_header(file_name, name_constants)

    # parse source file to get sensor definitions
    sensor_list = []
    for file_name in source_file_names:
        sensor_list += parse_file(args.kernel, file_name, name_constants)

    # sort by vendor_name, then by vendor_part_number
    sensor_list.sort(key=lambda sensor: get_sensor_sort_key(sensor))

    # generate json data file
    with open(args.website + '/_data/sensors.json', 'w') as out_file:
        print(json.dumps(sensor_list, sort_keys=True, indent=4), file=out_file)

    # generate markdown files, one for each sensor type
    for idx, item in enumerate(sensor_list):
        dest_file = '{0}/docs/sensors/{1}.markdown'.format(args.website, item['url_name'])
        with open(dest_file, 'w') as out_file:
            print('---', file=out_file)
            print('autogen:', 'This file was automatically generated by ' +
                    'sensors-defs-to-markdown.py', file=out_file)
            print('kernel_version:', kernel_version, file=out_file)
            print('source_file:', item['source_file'], file=out_file)
            print('source_line:', item['source_line'], file=out_file)
            print('title:', get_sensor_page_title(item), file=out_file)
            print('sensor_index:', idx, file=out_file)
            print('---', file=out_file)
            print('', file=out_file)
            print('{% include /docs/sensor.md %}', file=out_file)

if __name__ == '__main__':
    main()
