==========================================================
Vereinsverwaltung der Leuna-Bungalowgemeinschaft Roter-See
==========================================================

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/sweh/sw.allotmentclub/blob/master/LICENSE.txt
   :alt: License

.. image:: https://circleci.com/gh/sweh/sw.allotmentclub.svg?style=shield&circle-token=071a8316cb1ad9342d2bb4d3c316d548d12a292f
   :target: https://circleci.com/gh/sweh/sw.allotmentclub
   :alt: CircleCi

.. image:: https://codecov.io/github/sweh/sw.allotmentclub/coverage.svg?token=R4t7l3Pb0z&branch=master
   :target: https://codecov.io/github/sweh/sw.allotmentclub?branch=master
   :alt: CodeCov

.. image:: https://api.codacy.com/project/badge/grade/7c19e43c4fd746cc9834142edc77fbda
   :target: https://www.codacy.com
   :alt: Codacy

.. image:: https://sslbadge.org/?domain=verwaltung.roter-see.de
   :target: https://www.ssllabs.com/ssltest/analyze.html?d=verwaltung.roter-see.de
   :alt: SSL state

INSTALL
=======

Backend
*******

* Install and start postgres.

* Create the db with a current dump with ./db_restore.sh.

* Install nginx.

* Run the following commands to build and run the backend::

    virtualenv .
    source bin/activate
    pip install 3rdparty/gocept.loginuser-1.3a1.tar.gz
    pip install -r requirements.txt
    heroku local (or bin/start-nginx ./run.sh)

Testing
*******

* To run the tests in backend, first install the test requirements::

    pip install -r requirements/test.txt

* Run the backend tests::

    py.test
