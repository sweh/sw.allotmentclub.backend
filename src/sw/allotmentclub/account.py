from __future__ import unicode_literals

from datetime import date, timedelta

import kontocheck
import pyramid.threadlocal
import sqlalchemy.orm
import transaction
from fints.client import FinTS3PinTanClient, FinTSClientMode, NeedTANResponse
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from .log import auth_log, log_with_user
from .model import Object, Organization


class BankingAccount(Object):
    """Ein Bankkonto."""

    number = Column(String(10))
    name = Column(String(30))
    last_import = Column(DateTime)


class BookingKind(Object):
    """Ein Buchungstyp."""

    title = Column(String(50), nullable=False)
    shorttitle = Column(String(10), nullable=True)
    banking_account_id = Column(
        Integer, ForeignKey("bankingaccount.id"), nullable=True
    )
    banking_account = sqlalchemy.orm.relation(
        "BankingAccount", uselist=False, backref="booking_kinds"
    )


class Budget(Object):
    """Ein Element im Wirtschaftsplan."""

    value = Column(Integer)
    accounting_year = Column(Integer)
    booking_kind_id = Column(
        Integer, ForeignKey("bookingkind.id"), nullable=False
    )
    booking_kind = sqlalchemy.orm.relation("BookingKind", backref="budgets")


class Booking(Object):
    """Eine Buchung."""

    banking_account_id = Column(
        Integer, ForeignKey("bankingaccount.id"), nullable=False
    )
    banking_account = sqlalchemy.orm.relation(
        "BankingAccount", uselist=False, backref="bookings"
    )

    booking_day = Column(Date)
    booking_text = Column(String)
    purpose = Column(String)
    recipient = Column(String)
    iban = Column(String(34))
    bic = Column(String(11))
    value = Column(Integer)

    is_splitted = Column(Boolean, default=False, nullable=False)
    splitted_from_id = Column(Integer, ForeignKey("booking.id"), nullable=True)
    accounting_year = Column(Integer)
    ignore_in_reporting = Column(Boolean, default=False, nullable=False)

    member_id = Column(Integer, ForeignKey("member.id"), nullable=True)
    member = sqlalchemy.orm.relation(
        "Member", uselist=False, backref="bookings"
    )
    kind_id = Column(Integer, ForeignKey("bookingkind.id"), nullable=True)
    kind = sqlalchemy.orm.relation("BookingKind", uselist=False)

    def split(self, new_value):
        value = self.value if self.value is not None else 0
        if value > 0 and new_value < 0:
            return "Neuer Wert muss positiv sein."
        if value < 0 and new_value > 0:
            return "Neuer Wert muss negativ sein."
        if value > 0 and new_value >= self.value:
            return "Neuer Wert ist zu groß."
        if value < 0 and new_value <= self.value:
            return "Neuer Wert ist zu klein."
        if new_value == 0:
            return "Neuer Wert muss größer oder kleiner 0 sein."
        result = []
        for value in [new_value, self.value - new_value]:
            result.append(
                Booking.create(
                    banking_account=self.banking_account,
                    booking_day=self.booking_day,
                    booking_text=self.booking_text,
                    purpose=self.purpose,
                    recipient=self.recipient,
                    iban=self.iban,
                    bic=self.bic,
                    accounting_year=self.accounting_year,
                    value=value,
                    splitted_from_id=self.id,
                    member=self.member,
                    kind=self.kind,
                )
            )
        self.is_splitted = True
        return result


class SEPASammler(Object):
    """Ein SEPASammler."""

    pmtinfid = Column(String(100))
    booking_day = Column(Date)
    accounting_year = Column(Integer)
    kind_id = Column(Integer, ForeignKey("bookingkind.id"), nullable=True)
    kind = sqlalchemy.orm.relation("BookingKind", uselist=False)
    is_ueberweisung = Column(Boolean, default=False, nullable=False)


class SEPASammlerEntry(Object):
    """Defines which members are active in a SEPA Sammler."""

    sepa_sammler_id = Column(
        Integer, ForeignKey("sepasammler.id"), nullable=True
    )
    sepasammler = sqlalchemy.orm.relation(
        "SEPASammler", uselist=False, backref="entries"
    )
    ignore_in_reporting = Column(Boolean, default=False, nullable=False)
    member_id = Column(Integer, ForeignKey("member.id"), nullable=True)
    member = sqlalchemy.orm.relation("Member", uselist=False)
    value = Column(Integer)


class GrundsteuerB(Object):
    parcel_id = Column(Integer, ForeignKey("parcel.id"), nullable=False)
    parcel = sqlalchemy.orm.relation("Parcel", uselist=False)
    value = Column(Integer)


class Abwasser(Object):
    parcel_id = Column(Integer, ForeignKey("parcel.id"), nullable=False)
    parcel = sqlalchemy.orm.relation("Parcel", uselist=False)
    value = Column(Integer)


def create_fints_client():
    settings = pyramid.threadlocal.get_current_registry().settings
    return FinTS3PinTanClient(
        settings.get("banking.blz"),
        settings.get("banking.kto"),
        settings.get("banking.pin"),
        settings.get("banking.url"),
        mode=FinTSClientMode.INTERACTIVE,
        product_id=settings.get("banking.product_id"),
    )


def ask_for_tan(client, response, user=None):
    log_with_user(
        auth_log.info,
        user,
        "hat Bank-Import ausgeführt: Fehler ({}).".format(response.challenge),
    )
    transaction.commit()
    raise NotImplementedError("A TAN is required")
    tan = None
    client.send_tan(response, tan)


def import_transactions_from_fints(user=None):
    kontocheck.lut_load(9)
    client = create_fints_client()
    with client:
        if client.init_tan_response:
            ask_for_tan(client, client.init_tan_response, user)
        accounts = client.get_sepa_accounts()
        if isinstance(accounts, NeedTANResponse):
            accounts = ask_for_tan(client, accounts, user)
        for account in accounts:
            try:
                local_account = (
                    BankingAccount.query()
                    .filter(BankingAccount.number == account.accountnumber)
                    .one()
                )
            except sqlalchemy.orm.exc.NoResultFound:
                continue
            statements = client.get_transactions(
                account, date.today() - timedelta(days=50), date.today()
            )
            while isinstance(statements, NeedTANResponse):
                statements = ask_for_tan(client, statements, user)
            import_transactions(
                [stmt.data for stmt in statements], local_account, user
            )


def import_transactions(statements, account, user=None):
    count = 0
    for id, statement in enumerate(statements):
        try:
            result = add_transaction(statement, account)
        except Exception as e:
            log_with_user(
                auth_log.info,
                user,
                "hat Bank-Import ausgeführt: Fehler ({}).".format(e),
            )
            transaction.commit()
            raise
        if isinstance(result, int):
            count += result
    if count and user:
        log_with_user(
            auth_log.info,
            user,
            "hat Bank-Import ausgeführt: {} neue Buchungen.".format(count),
        )
    transaction.commit()


def get_sepa_sammlers(data, account):
    if data["posting_text"] != "SAMMEL-LS-EINZUG":
        return
    pmtinfid = data["customer_reference"].splitlines()[1]
    try:
        sepasammler = (
            SEPASammler.query()
            .filter(SEPASammler.pmtinfid == pmtinfid)
            .filter(SEPASammler.organization_id == account.organization_id)
            .one()
        )
    except Exception:
        raise ValueError(
            "Keine Sammler zu PmtInfId '{}' gefunden.".format(pmtinfid)
        )
    sammlers = (
        SEPASammlerEntry.query()
        .filter(SEPASammlerEntry.sepasammler == sepasammler)
        .filter(SEPASammlerEntry.organization_id == account.organization_id)
        .all()
    )
    if not sammlers:
        raise ValueError(
            "Keine Sammler-Einträge zu PmtInfId '{}' gefunden.".format(
                pmtinfid
            )
        )
    return sammlers


def add_transaction(data, account):
    from sw.allotmentclub import Member

    accounting_year = data["date"].year
    org_title = None
    org = Organization.get(account.organization_id)
    if org:
        org_title = org.title
    if data["currency"] != "EUR":
        raise ValueError(
            "Couldn't import booking {} because its not in Eur.".format(
                data["purpose"]
            )
        )
    value = int(data["amount"].amount * 10000)
    sammlers = get_sepa_sammlers(data, account)
    booking = Booking.find_or_create(
        organization_id=account.organization_id,
        banking_account=account,
        booking_day=data["date"],
        purpose=data["purpose"],
        recipient=(
            data["applicant_name"]
            if data["applicant_name"] is not None
            else org_title
        ),
        value=value,
    )
    if booking.id:
        return
    booking.accounting_year = accounting_year
    booking.booking_text = data["posting_text"]
    booking.iban = data["applicant_iban"]
    booking.bic = data["applicant_bin"]
    if booking.iban:
        try:
            booking.member = (
                Member.query()
                .filter(Member.iban == booking.iban)
                .filter(Member.organization_id == booking.organization_id)
                .one()
            )
        except Exception:
            pass
    if booking.member:
        try:
            debit_booking = (
                Booking.query()
                .filter(Booking.value == 0 - booking.value)
                .filter(Booking.member == booking.member)
                .filter(Booking.accounting_year == booking.accounting_year)
                .filter(Booking.organization_id == booking.organization_id)
                .one()
            )
        except Exception:
            pass
        else:
            booking.kind = debit_booking.kind
    if booking.booking_text == "SAMMEL-LS-EINZUG":
        if not booking.recipient:
            booking.recipient = org_title
        sum_ = 0
        for sammler in sammlers:
            sum_ += sammler.value
        if (booking.value - 100) > sum_:
            imported, open_ = booking.split(sum_)
            imported.booking_text = imported.booking_text + " Verrechnet"
            open_.organization_id = booking.organization_id
            imported.organization_id = booking.organization_id
        sum_ += sammler.value
    return 1
