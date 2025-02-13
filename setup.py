"""The allotmentclub portal"""

import glob

from setuptools import find_packages, setup

exec(open("src/sw/allotmentclub/version.py").read())

setup(
    name="sw.allotmentclub",
    version=__version__,  # noqa
    install_requires=[
        "pyramid",
        "fints",
        "sepaxml",
    ],
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "paste.app_factory": [
            "portal=sw.allotmentclub.browser.app:factory",
        ],
        "console_scripts": [
            "import_members = sw.allotmentclub.scripts:import_members",
            "import_transactions = sw.allotmentclub.scripts:"
            "import_transactions",
            "export_members_vcf = sw.allotmentclub.scripts:"
            "export_members_vcf",
            "export_events_ics = sw.allotmentclub.scripts:"
            "export_events_ics",
        ],
    },
    author="Sebastian Wehrmann",
    author_email="sebastian@wehrmann.it",
    license="ZPL 2.1",
    url="https://github.com/sweh/sw.allotmentclub",
    keywords="",
    classifiers="""\
        License :: OSI Approved :: Zope Public License
        Programming Language :: Python
        Programming Language :: Python :: 3.6
        Programming Language :: Python :: 3 :: Only
        Framework :: Pyramid
        Topic :: Internet :: WWW/HTTP
        Topic :: Internet :: WWW/HTTP :: WSGI :: Application
"""[:-1].split("\n"),
    platforms=["unix", "darwin"],
    description=__doc__.strip(),
    long_description=(
        open("README.rst").read() + "\n\n" + open("CHANGES.rst").read()
    ),
    namespace_packages=["sw"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    data_files=[("", glob.glob("*.rst"))],
    zip_safe=False,
)
