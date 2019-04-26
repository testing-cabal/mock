import re
from argparse import ArgumentParser
from os.path import dirname, abspath
from subprocess import check_output, call


def git(command, repo):
    return check_output('git '+command, cwd=repo, shell=True).decode()


def repo_state_bad(mock_repo):
    status = git('status', mock_repo)
    if 'You are in the middle of an am session' in status:
        print(f'Mock repo at {mock_repo} needs cleanup:\n')
        call('git status', shell=True)
        return True


def cleanup_old_patches(mock_repo):
    print('cleaning up old patches:')
    call('rm -vf /tmp/*.mock.patch', shell=True)
    call('find . -name "*.rej" -print -delete', shell=True, cwd=mock_repo)


def find_initial_cpython_rev():
    with open('lastsync.txt') as source:
        return source.read().strip()


def cpython_revs_affecting_mock(cpython_repo, start):
    revs = git(f'log --no-merges --format=%H {start}..  '
               f'-- Lib/unittest/mock.py Lib/unittest/test/testmock/',
               repo=cpython_repo).split()
    revs.reverse()
    print(f'{len(revs)} patches to backport')
    return revs


def has_been_backported(mock_repo, cpython_rev):
    backport_rev = git(f'log --format=%H --grep "Backports: {cpython_rev}"',
                       repo=mock_repo).strip()
    if backport_rev:
        print(f'{cpython_rev} backported in {backport_rev}')
        return True
    print(f'{cpython_rev} has not been backported')


def extract_patch_for(cpython_repo, rev):
    return git(f'format-patch -1 --no-stat --keep-subject --signoff --stdout {rev}',
               repo=cpython_repo)


def munge(rev, patch):

    sign_off = 'Signed-off-by:'
    patch = patch.replace(sign_off, f'Backports: {rev}\n{sign_off}', 1)

    for pattern, sub in (
        ('(a|b)/Lib/unittest/mock.py', r'\1/mock/mock.py'),
        ('(a|b)/Lib/unittest/test/testmock/(.+)', r'\1/mock/tests/\2'),
        ('(a|b)/Misc/NEWS', r'\1/NEWS'),
    ):
        patch = re.sub(pattern, sub, patch)
    return patch


def apply_patch(mock_repo, rev, patch):
    patch_path = f'/tmp/{rev}.mock.patch'

    with open(patch_path, 'w') as target:
        target.write(patch)
    print(f'wrote {patch_path}')

    call(f'git am -k --reject {patch_path}', cwd=mock_repo, shell=True)


def main():
    args = parse_args()

    if repo_state_bad(args.mock):
        return

    cleanup_old_patches(args.mock)

    initial_cpython_rev = find_initial_cpython_rev()

    revs = cpython_revs_affecting_mock(args.cpython, initial_cpython_rev)
    for rev in revs:

        if has_been_backported(args.mock, rev):
            continue

        patch = extract_patch_for(args.cpython, rev)
        patch = munge(rev, patch)
        apply_patch(args.mock, rev, patch)
        break


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--cpython', default='../cpython')
    parser.add_argument('--mock', default=abspath(dirname(__file__)))
    return parser.parse_args()


if __name__ == '__main__':
    main()
