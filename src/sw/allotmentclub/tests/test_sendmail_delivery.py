from repoze.sendmail.delivery import MailDataManager
from repoze.sendmail.tests.test_delivery import DummyTransaction
import pytest


@pytest.mark.xfail
def test_abort_w_TPC_does_not_raise_ValueError():
    mdm = MailDataManager(object, (), None)
    txn = DummyTransaction()
    mdm.join_transaction(txn)
    mdm.tpc_phase = 1
    mdm.abort(txn)
