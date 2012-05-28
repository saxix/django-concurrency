VERSION = __version__ = (0, 1, 0, 'final', 0)
__author__ = 'sax'


def get_version(version=None):
    """Derives a PEP386-compliant version number from VERSION."""
    if version is None:
        version = VERSION
    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        import concurrency
        path =  concurrency.__path__[0]
        head_path = '%s/../.git/logs/HEAD' % path
        try:
            for line in open(head_path):pass
            revision = line.split()[0]
        except IOError:
            raise Exception('Alpha version is are only allowed as git clone')
        sub = '.dev%s' % revision

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub
