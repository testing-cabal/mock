import re
from glob import glob
from os.path import join
from subprocess import call

import blurb as blurb_module
from argparse import ArgumentParser
from mock import version_info

VERSION_TYPES = ['major', 'minor', 'bugfix']


def incremented_version(version_info, type_):
    type_index = VERSION_TYPES.index(type_)
    version_info = tuple(e+(1 if i==type_index else 0)
                         for i, e in enumerate(version_info))
    return '.'.join(str(p) for p in version_info)


def text_from_news():
    # hack:
    blurb_module.sections.append('NEWS.d')

    blurbs = blurb_module.Blurbs()
    for path in glob(join('NEWS.d', '*')):
        blurbs.load_next(path)

    text = []
    for metadata, body in blurbs:
        bpo = metadata['bpo']
        body = f"- Issue #{bpo}: " + body
        text.append(blurb_module.textwrap_body(body, subsequent_indent='  '))

    return '\n'.join(text)


def news_to_changelog(version):
    with open('CHANGELOG.rst') as source:
        current_changelog = source.read()

    text = [version]
    text.append('-'*len(version))
    text.append('')
    text.append(text_from_news())
    text.append(current_changelog)

    new_changelog = '\n'.join(text)
    with open('CHANGELOG.rst', 'w') as target:
        target.write(new_changelog)


def update_version(new_version):
    path = join('mock', 'mock.py')
    with open(path) as source:
        text = source.read()

    text = re.sub("(__version__ = ')[^']+(')",
                  r"\g<1>"+new_version+r"\2",
                  text)

    with open(path, 'w') as target:
        target.write(text)


def git(command):
    return call('git '+command, shell=True)


def git_commit(new_version):
    git('rm NEWS.d/*')
    git('add CHANGELOG.rst')
    git('add mock/mock.py')
    git(f'commit -m "Preparing for {new_version} release."')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('type', choices=VERSION_TYPES)
    return parser.parse_args()


def main():
    args = parse_args()
    new_version = incremented_version(version_info, args.type)
    news_to_changelog(new_version)
    update_version(new_version)
    git_commit(new_version)
    print(f'{new_version} ready to push, please check the HEAD commit first!')


if __name__ == '__main__':
    main()
