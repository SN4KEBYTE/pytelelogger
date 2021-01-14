from pathlib import Path
from setuptools import setup, find_packages

from pytelelogger import __version__

CWD: Path = Path(__file__).parent
README: str = (CWD / 'README.md').read_text(encoding='utf-8', errors='ignore')

setup(
    name='pytelelogger',
    version=__version__,

    description='Use Telegram bots to track your project logs in real-time.',
    long_description=README,
    long_description_content_type='text/markdown',

    url='https://github.com/SN4KEBYTE/pytelelogger',
    author='Timur Kasimov',
    license='GNU General Public License v3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Typing :: Typed'
    ],

    install_requires=[
        'python-telegram-bot>=13.1',
        'pyyaml>=5.3.1'
    ],
    packages=find_packages(),
)