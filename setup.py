import codecs
from codecs import open
from os import path, system
from sys import argv, exit

from setuptools import setup, find_packages

__version__ = '1.0.0'

here = path.abspath(path.dirname(__file__))

# Shortcut for building/publishing to Pypi
if argv[-1] == 'publish':
    system('python setup.py sdist bdist_wheel upload')
    exit()


def parse_reqs(req_path='./requirements.txt'):
    """Recursively parse requirements from nested pip files."""
    req = []
    with codecs.open(req_path, 'r') as handle:
        # remove comments and empty lines
        lines = (line.strip() for line in handle
                 if line.strip() and not line.startswith('#'))

        for line in lines:
            # check for nested requirements files
            if line.startswith('-r'):
                # recursively call this function
                req += parse_reqs(req_path=line[3:])

            else:
                # add the line as a new requirement
                req.append(line)

    return req


def parse_readme():
    """Parse contents of the README."""
    # Get the long description from the relevant file
    readme_path = path.join(here, 'README.md')
    with codecs.open(readme_path, encoding='utf-8') as handle:
        desc = handle.read()

    return desc


# get the dependencies and installs
all_reqs = parse_reqs()


install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='subscribe-ssr',

    version=__version__,

    description='update ssr configuration file via subscription link',
    long_description=parse_readme(),
    keywords='shadowsocksr ssr',
    author='genzj',
    author_email='zj0512@gmail.com',
    license='BSD',

    url='https://github.com/genzj/subscribe-ssr',
    download_url='https://github.com/genzj/subscribe-ssr/tarball/' + __version__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: Proxy Servers',
        'Topic :: Terminals',
    ],
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,

    test_suite='tests',

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and
    # allow pip to create the appropriate form of executable for the
    # target platform.
    entry_points=dict(
        console_scripts=[
            'subssr = subssr.main:cli',
        ],
    ),
)
