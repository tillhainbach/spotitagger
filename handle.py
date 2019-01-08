import logging
import yaml
import argparse
import os
import sys


_LOG_LEVELS_STR = ['INFO', 'WARNING', 'ERROR', 'DEBUG']

default_conf = { 'spotitagger':
                 { 'folder'                 : None,
                   'overwrite-metadata'     : True,
                   'log-level'              : 'INFO',
                   'username'               :  None }
               }


def log_leveller(log_level_str):
    loggin_levels = [logging.INFO, logging.WARNING, logging.ERROR, logging.DEBUG]
    log_level_str_index = _LOG_LEVELS_STR.index(log_level_str)
    loggin_level = loggin_levels[log_level_str_index]
    return loggin_level

def merge(default, config):
    """ Override default dict with config dict. """
    merged = default.copy()
    merged.update({ k: v for k,v in config.items() if v })
    return merged

def get_config(config_file):
    try:
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
    except FileNotFoundError:
        with open(config_file, 'w') as ymlfile:
            yaml.dump(default_conf, ymlfile, default_flow_style=False)
            cfg = default_conf
    return cfg['spotitagger']


def override_config(config_file, parser, raw_args=None):
    """ Override default dict with config dict passed as command line argument. """
    config_file = os.path.realpath(config_file)
    config = merge(default_conf['spotiftagger'], get_config(config_file))

    parser.set_defaults(file_format=config['file-format'])
    parser.set_defaults(folder=os.path.relpath(config['folder'], os.getcwd()))
    parser.set_defaults(log_level=config['log-level'])

    return parser.parse_args(raw_args)

def string_to_boolean(string):
    if string.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif string.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        return string

def get_arguments(raw_args = None, to_group = True, to_merge = True):
    parser = argparse.ArgumentParser(
        description = 'Update your id3-tags based on Spotify metadata.',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    if to_merge:
        config_file = os.path.join(sys.path[0], 'config.yml')
        config = merge(default_conf['spotitagger'], get_config(config_file))
    else:
        config = default_conf['spotitagger']

    if to_group:
        group = parser.add_mutually_exclusive_group(required = True)

        group.add_argument(
            '-p', '--playlist', help='tag songs based on preexisting Spotify playlist')

    default_folder = config['folder']
    if default_folder:
        parser.add_argument(
            '-f', '--folder', default=os.path.relpath(default_folder, os.getcwd()),
                help = 'path to folder where songs are stored in', required = True)
    else:
        parser.add_argument(
            '-f', '--folder', help = 'path to folder where songs are stored in',
            required = True)
    parser.add_argument(
        '-ll', '--log-level', default=config['log-level'],
        choices = _LOG_LEVELS_STR,
        type = str.upper,
        help = 'set log verbosity')
    parser.add_argument(
        '-c', '--config', default = None,
        help = 'Replace with custom config.yml file')
    parser.add_argument(
        '-o', '--overwrite', default = config['overwrite-metadata'],
        type=string_to_boolean, choices = [True, False, 'merge'],
        help = 'overwrite existing metadata infos. Options are True, False, merge')
    parser.add_argument(
        '-u', '--username', default = config['username'],
        help = 'your spotify username')

    parsed = parser.parse_args(raw_args)

    if parsed.config is not None and to_merge:
        parsed = override_config(parsed.config,parser)

    parsed.log_level = log_leveller(parsed.log_level)

    return parsed
