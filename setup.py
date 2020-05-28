"""The allotmentclub portal"""

from setuptools import setup, find_packages
import glob

exec(open("src/sw/allotmentclub/version.py").read())

setup(
    name='sw.allotmentclub',
    version=__version__,  # noqa

    install_requires=[
        'pyramid',
        'fints',
    ],

    extras_require={
        'test': [
            'pytest',
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
