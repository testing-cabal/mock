import re
from argparse import ArgumentParser
from os.path import dirname, abspath, join
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
    print(f'{len(revs)} patches that may need backporting')
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
        (r'(a|b)/Lib/unittest/test/testmock/(\S+)', r'\1/mock/tests/\2'),
        ('(a|b)/Misc/NEWS', r'\1/NEWS'),
        ('(a|b)/NEWS.d/next/[^/]+/(.+\.rst)', r'\1/NEWS.d/\2'),
    ):
        patch = re.sub(pattern, sub, patch)
    return patch


def apply_patch(mock_repo, rev, patch):
    patch_path = f'/tmp/{rev}.mock.patch'

    with open(patch_path, 'w') as target:
        target.write(patch)
    print(f'wrote {patch_path}')

    call(f'git am -k '
         f'--include "mock/*" --include NEWS --include "NEWS.d/*" '
         f'--reject {patch_path} ',
         cwd=mock_repo, shell=True)


def update_last_sync(mock_repo, rev):
    with open(join(mock_repo, 'lastsync.txt'), 'w') as target:
        target.write(rev+'\n')
    print(f'update lastsync.txt to {rev}')


def rev_from_mock_patch(text):
    match = re.search('Backports: ([a-z0-9]+)', text)
    return match.group(1)


def skip_current(mock_repo, reason):
    text = git('am --show-current-patch', repo=mock_repo)
    rev = rev_from_mock_patch(text)
    git('am --abort', repo=mock_repo)
    print(f'skipping {rev}')
    update_last_sync(mock_repo, rev)
    call(f'git commit -m "Backports: {rev}, skipped: {reason}" lastsync.txt', shell=True, cwd=mock_repo)
    cleanup_old_patches(mock_repo)


def commit_last_sync(revs, mock_repo):
    print('Yay! All caught up!')
    if len(revs):
        git('commit -m "latest sync point" lastsync.txt', repo=mock_repo)


def main():
    args = parse_args()

    if args.skip_current:
        return skip_current(args.mock, args.skip_reason)

    if repo_state_bad(args.mock):
        return

    cleanup_old_patches(args.mock)

    initial_cpython_rev = find_initial_cpython_rev()

    revs = cpython_revs_affecting_mock(args.cpython, initial_cpython_rev)
    for rev in revs:

        if has_been_backported(args.mock, rev):
            update_last_sync(args.mock, rev)
            continue

        patch = extract_patch_for(args.cpython, rev)
        patch = munge(rev, patch)
        apply_patch(args.mock, rev, patch)
        break

    else:
        commit_last_sync(revs, args.mock)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--cpython', default='../cpython')
    parser.add_argument('--mock', default=abspath(dirname(__file__)))
    parser.add_argument('--skip-current', action='store_true')
    parser.add_argument('--skip-reason', default='it has no changes needed here.')
    return parser.parse_args()


if __name__ == '__main__':
    main()
