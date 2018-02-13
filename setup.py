"""The allotmentclub portal"""

from setuptools import setup, find_packages
import glob
import sys

exec(open("src/sw/allotmentclub/version.py").read())

def read(path):
    if sys.version_info < (3,):
        f = open(path)
    else:
        f = open(path, encoding='UTF-8')
    text = f.read()
    f.close()
    return text


setup(
    name='sw.allotmentclub',
    version=__version__,  # noqa

    install_requires=[
        'bcrypt',
        'beautifulsoup4',
        'gocept.logging>=0.3',
        'gocept.loginuser>=1.3a1',
        'risclog.sqlalchemy>=3.0',
        'setuptools',
        'fints',
        'sqlalchemy',
        'transaction',
        'zope.component',
        'zope.interface',
        'user-agents',
        'markdown',
        'lnetatmo',
        'pybars3',
        'pyPdf2',
        'xhtml2pdf',
        'Babel',
        'kontocheck',
        'mt-940',
    ],

    extras_require={
        'test': [
            'gocept.cache',
            'gocept.testdb>=1.1.1',
            'gocept.testing',
            'mock',
            'webtest',
            'z3c.etestbrowser',
        ],
        'web': [
            'python-dateutil',
            'gocept.cache',
            'pyramid',
            'pyramid_beaker',
            'pyramid_exclog',
            'pyramid_mailer',
            'python-magic',
            'repoze.vhm',
        ],
    },

    entry_points={
        'paste.app_factory': [
            'portal=sw.allotmentclub.browser.app:factory',
        ],
        'console_scripts': [
            'import_members = sw.allotmentclub.scripts:import_members',
            'import_transactions = sw.allotmentclub.scripts:'
            'import_transactions',
            'export_members_vcf = sw.allotmentclub.scripts:'
            'export_members_vcf'
        ],
    },

    author='Sebastian Wehrmann',
    author_email='sebastian@wehrmann.it',
    license='ZPL 2.1',
    url='https://github.com/sweh/sw.allotmentclub',

    keywords='',
    classifiers="""\
        License :: OSI Approved :: Zope Public License
        Programming Language :: Python
        Programming Language :: Python :: 3.5
        Programming Language :: Python :: 3.6
        Programming Language :: Python :: 3 :: Only
        Framework :: Pyramid
        Topic :: Internet :: WWW/HTTP
        Topic :: Internet :: WWW/HTTP :: WSGI :: Application
"""[:-1].split('\n'),
    description=__doc__.strip(),
    namespace_packages=['sw'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    data_files=[('', glob.glob('*.rst'))],
    zip_safe=False,
)
