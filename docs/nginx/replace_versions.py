#!/usr/bin/env python

import os
import sys
import argparse
import copy
import logging
import logging.handlers

from functools import cmp_to_key
from collections import OrderedDict
from packaging import version
from bs4 import BeautifulSoup

SOURCE_EXT = '.html'
VERSIONS_CONTAINER_SELECTOR = 'div.rst-other-versions > dl'
VERSIONS_HEADER_SELECTOR = 'dt'
VERSIONS_SELECTOR = 'dd'

def init_logger(level):
    # Setup logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_logger(level))
    return logger


def get_logger(level=logging.INFO):
    return init_logger(level)


def stdout_logger(level):
    console = logging.StreamHandler(sys.stdout)
    if isinstance(level, str):
        level = level.upper()
    console.setLevel(level)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    return console


class Parser(object):

    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument(
            'docs_parent_path',
            help='Parent directory of '
        )

    def parse(self, *args):
        return self._parser.parse_args(args)


def read_html(path):
    with open(path, 'r') as fl:
        return BeautifulSoup(fl.read(), 'lxml')


def get_container_tag(html):
    return html.select_one(VERSIONS_CONTAINER_SELECTOR)


def get_header_tag(container):
    return container.select_one(VERSIONS_HEADER_SELECTOR)


def get_version_tag(container):
    return container.select_one(VERSIONS_SELECTOR)


def get_version_tags(container):
    return container.select(VERSIONS_SELECTOR)


def write_html(html, path):
    with open(path, 'w') as fl:
        fl.write(str(html))


def get_files_list(path):
    files = OrderedDict()

    logger.info('Reading source files')
    for root, _folders, file_names in os.walk(path):
        if root == path:
            continue

        for file in file_names:
            target_file = os.path.join(root, file)
            _basename, ext = os.path.splitext(target_file)

            if ext != SOURCE_EXT:
                continue

            logger.info('  File {path}'.format(path=target_file))

            target = read_html(target_file)
            container = get_container_tag(target)
            existing_versions = get_version_tags(container)

            if not existing_versions:
                logger.info('    Skipped')
                continue

            files[target_file] = target
            logger.info('    OK')

    return files


def get_versions(files, root):
    print(root)
    versions = set()
    for file in files.keys():
        dir_name = file.replace(root+os.sep, '').replace(root, '').split(os.sep)[0]
        if dir_name != 'latest':
            versions.add(version.parse(dir_name))

    return ['latest'] + [str(ver) for ver in reversed(sorted(list(versions)))]


def write_versions(versions, target, file):
    logger.info('Writing target file {path}'.format(path=file))

    container = get_container_tag(target)
    header = copy.copy(get_header_tag(target))

    versions_tags = []
    for version in versions:
        version_tag = copy.copy(get_version_tag(container))
        version_tag.a.attrs['href'] = '/{}/'.format(version)
        version_tag.a.string = version
        versions_tags.append(version_tag)

    container.clear()
    container.append(header)
    container.extend(versions_tags)

    write_html(target, file)

    logger.info('  OK')


def replace_versions_list(args, logger):
    docs_parent_path = os.path.abspath(args.docs_parent_path)

    files = get_files_list(docs_parent_path)
    if not files:
        logger.error('No files found!')
        exit(1)

    versions = get_versions(files, docs_parent_path)
    for file, target in files.items():
        write_versions(versions, target, file)

    logger.info('Success!')


if __name__ == '__main__':
    parser = Parser()
    args = parser.parse(*sys.argv[1:])

    log_level = 'INFO'
    logger = get_logger(log_level)

    replace_versions_list(args, logger)
