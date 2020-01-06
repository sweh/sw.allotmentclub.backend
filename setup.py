"""The allotmentclub portal"""

from setuptools import setup, find_packages
import glob

exec(open("src/sw/allotmentclub/version.py").read())

setup(
    name='sw.allotmentclub',
    version=__version__,  # noqa

    install_requires=[
        'Babel==2.4.0',
        'alembic==1.0.0',
        'apipkg == 1.4',
        'bcrypt==3.1.3',
        'beaker==1.8.1',
        'beautifulsoup4 == 4.6.0',
        'beautifulsoup4==4.6.0',
        'cffi==1.10.0',
        'click==6.7',
        'codecov == 2.0.10',
        'decorator==4.0.11',
        'fints==2.2.0',
        'first==2.0.1',
        'funcsigs==1.0.2',
        'gocept.logging==0.8.1',
        'gocept.loginuser==1.3',
        'html5lib==1.0b10',
        'img2pdf==0.3.3',
        'kontocheck==5.10.0',
        'passlib==1.7.1',
        'lnetatmo==1.4.3',
        'mako==1.0.6',
        'markdown==2.6.8',
        'markupsafe==1.0',
        'mt-940==4.10.0',
        'openpyxl==2.4.8',
        'paste==2.0.3',
        'pastedeploy==2.0.1',
        'pastescript==2.0.2',
        'pillow==6.2.1',
        'sentry_sdk==0.13.1',
        'pipdeptree==0.10.1',
        'psycopg2-binary==2.7.5',
        'py == 1.5.2',
        'pybars3==0.9.3',
        'pycparser==2.17',
        'pymeta3==0.5.1',
        'pypdf2==1.26.0',
        'pyramid-beaker==0.8',
        'pyramid-exclog==1.0',
        'pyramid-mailer==0.15.1',
        'pyramid-tm==2.2',
        'pyramid-who==0.3',
        'pyramid==1.9.2',
        'python-dateutil==2.6.0',
        'python-editor==1.0.3',
        'pytz==2017.2',
        'radicale==1.1.2',
        'reportlab==3.4.0',
        'repoze.lru==0.6',
        'repoze.sendmail==4.4.1',
        'repoze.who==2.3',
        'requests==2.22.0',
        'risclog.sqlalchemy==3.0',
        'six==1.10.0',
        'sqlalchemy==1.3.0',
        'svglib == 0.8.1',
        'transaction==2.2.1',
        'translationstring==1.3',
        'ua-parser==0.7.3',
        'user-agents==1.1.0',
        'venusian==1.1.0',
        'waitress==1.4.2',
        'webob==1.7.2',
        'xhtml2pdf==0.2b1',
        'xlrd == 1.1.0',
        'xlsxwriter==0.9.6',
        'zope.component==4.3.0',
        'zope.configuration==4.1.0',
        'zope.deprecation==4.2.0',
        'zope.event==4.2.0',
        'zope.exceptions==4.1.0',
        'zope.i18nmessageid==4.1.0',
        'zope.interface==4.4.1',
        'zope.schema==4.4.2',
        'zope.sqlalchemy==1.0',
        'zope.testbrowser == 5.2.4',
    ],

    extras_require={
        'test': [
            'coverage == 4.4.2',
            'execnet == 1.5.0',
            'gocept.testdb == 1.3',
            'mock == 2.0.0',
            'pdf-diff3==0.9.3',
            'pep8 == 1.7.1',
            'pytest == 4.6.5',
            'pytest-cache == 1.0',
            'pytest-cov == 2.7.1',
            'pytest-flakes == 4.0.0',
            'pytest-pep8 == 1.0.6',
            'pytest-remove-stale-bytecode == 3.0.1',
            'pytest-rerunfailures == 7.0',
            'pytest-sugar == 0.9.2',
            'pytest-xdist == 1.29.0',
            'termcolor == 1.1.0',
            'unittest2 == 1.1.0',
            'webtest == 2.0.29',
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
            'grab_dashboard_data = sw.allotmentclub.scripts:'
            'grab_dashboard_data',
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
