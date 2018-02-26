==========================================================
Vereinsverwaltung der Leuna-Bungalowgemeinschaft Roter-See
==========================================================

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/sweh/sw.allotmentclub/blob/master/LICENSE.txt
   :alt: License

.. image:: https://api.codeclimate.com/v1/badges/fd997cfcf42412bf1cd6/test_coverage
   :target: https://codeclimate.com/github/sweh/sw.allotmentclub.backend/test_coverage
   :alt: Test Coverage

.. image:: https://api.codeclimate.com/v1/badges/fd997cfcf42412bf1cd6/maintainability
   :target: https://codeclimate.com/github/sweh/sw.allotmentclub.backend/maintainability
   :alt: Maintainability

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
