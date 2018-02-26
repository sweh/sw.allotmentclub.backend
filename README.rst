==========================================================
Vereinsverwaltung der Leuna-Bungalowgemeinschaft Roter-See
==========================================================

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/sweh/sw.allotmentclub.backend/blob/master/LICENSE.rst
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

Note: It is recommended to install this package via the deployment package
`sw.allotmentclub.deployment`.

* Install and start postgres.

* Create the db with a current dump (contained in the deployment package).

* Install nginx.

* Run the following commands to build and run the backend::

    virtualenv .
    source bin/activate
    pip install -e .
    bin/pserve portal.ini

Testing
=======

* To run the tests in backend, first install the test requirements::

    pip install -e .[test]

* Run the backend tests::

    py.test
