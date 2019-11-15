"""
Data collections mapping semantic units in the SEPA standard. Most of those
can be rendered to an XML representation.
"""

from datetime import datetime
from decimal import Decimal
from io import StringIO
from lxml.builder import ElementMaker
from lxml.etree import tostring, parse, XMLSchema
from pathlib import Path
import re


class PyPAINException(Exception):
    pass


class InvalidXMLException(PyPAINException):
    """Signifies XML that doesn't conform with the SEPA XML schema."""

    pass


class InvalidXMLValueException(PyPAINException):
    """Signifies values that don't conform with SEPA data types."""

    pass


class SEPAType:

    syntax = ""
    special_character_mapping = {
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "&": "+",
        "*": ".",
        "$": ".",
        "%": ".",
        "<": ".",
        ">": ".",
    }
    # Even though the SEPA scheme defines an UTF-8 encoding, only a small
    # subset is indeed valid. This may change.
    special_character_pattern = r"([^A-Za-z0-9\+|\?|/|\-|:|\(|\)|\.|,|\'| ])"
    special_character_fallback = "."

    def __init__(self, input_value, replace_special_chars=True):
        self.value = self.transform(input_value)
        if replace_special_chars:
            self.replace_special_characters()

        if not self.valid():
            raise InvalidXMLValueException(
                'Invalid value "{}" for type {}.'.format(
                    self.value, self.__class__.__name__
                )
            )

    @staticmethod
    def transform(input_value):
        """Transform input value to string representation."""
        return str(input_value)

    def replace_special_characters(self):
        for search, replace in self.special_character_mapping.items():
            self.value = self.value.replace(search, replace)
        self.value = re.sub(
            self.special_character_pattern,
            self.special_character_fallback,
            self.value,
        )

    def valid(self):
        """Return True if value is conform to the syntax of this type."""
        regex = re.compile(self.syntax)
        return regex.match(self.value) is not None

    @staticmethod
    def to_string(_, item):
        """Used by lxml's ETree to serialize values implicitly."""
        return item.value

    def __str__(self):
        return "{} <{}>".format(self.__class__.__name__, self.value)


class AnyBICIdentifier(SEPAType):
    """
    >>> AnyBICIdentifier('MARKDEFF').valid()
    True
    >>> AnyBICIdentifier('INVALID').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^[A-Z]{6,6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3,3}){0,1}$"


class BICIdentifier(SEPAType):
    """
    >>> BICIdentifier('MARKDEFF').valid()
    True
    >>> BICIdentifier('INVALID').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^[A-Z]{6,6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3,3}){0,1}$"


class CountryCode(SEPAType):
    """
    >>> CountryCode('DE').valid()
    True
    >>> CountryCode('A1').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^[A-Z]{2,2}$"


class ActiveOrHistoricCurrencyCode(SEPAType):
    """
    >>> ActiveOrHistoricCurrencyCode('USD').valid()
    True
    >>> ActiveOrHistoricCurrencyCode('DM').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^[A-Z]{3,3}$"


class ActiveOrHistoricCurrencyCodeEUR(SEPAType):
    """
    >>> ActiveOrHistoricCurrencyCodeEUR('EUR').valid()
    True
    >>> ActiveOrHistoricCurrencyCodeEUR('USD').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^EUR$"


class ActiveOrHistoricCurrencyAndAmountSEPA(SEPAType):
    """
    >>> ActiveOrHistoricCurrencyAndAmountSEPA('12345678901').valid()
    True
    >>> ActiveOrHistoricCurrencyAndAmountSEPA('0.12').valid()
    True
    >>> ActiveOrHistoricCurrencyAndAmountSEPA('0.1').valid()
    True
    >>> ActiveOrHistoricCurrencyAndAmountSEPA('-1').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> ActiveOrHistoricCurrencyAndAmountSEPA('0.123').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> ActiveOrHistoricCurrencyAndAmountSEPA(Decimal('1.1')).value
    '1.1'
    """

    syntax = r"^\d{1,11}(\.\d{1,2})?$"


class DecimalTime(SEPAType):
    """
    >>> DecimalTime('235959000').valid()
    True
    >>> DecimalTime('235959').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^[0-9]{9,9}$"


class IBAN2007Identifier(SEPAType):
    """
    >>> IBAN2007Identifier('KW81CBKU0000000000001234560101').valid()
    True
    >>> IBAN2007Identifier('NO8330001234567').valid()
    True
    >>> IBAN2007Identifier('DE12').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^[A-Z]{2,2}[0-9]{2,2}[a-zA-Z0-9]{1,30}$"


class Max1025Text(SEPAType):
    """
    >>> Max1025Text('A valid text.').valid()
    True
    >>> Max1025Text('A' * 1026).valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> Max1025Text('').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^.{1,1025}$"


class Max140Text(SEPAType):
    """
    >>> Max140Text('A valid text.').valid()
    True
    >>> Max140Text('A' * 141).valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> Max140Text('').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^.{1,140}$"


class Max15NumericText(SEPAType):
    """
    >>> Max15NumericText('1' * 15).valid()
    True
    >>> Max15NumericText('1' * 16).valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> Max15NumericText('').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> Max15NumericText(42).value  # Number types are fine.
    '42'
    """

    syntax = r"^[0-9]{1,15}$"


class Max35Text(SEPAType):
    """
    >>> Max35Text('1' * 35).valid()
    True
    >>> Max35Text('1' * 36).valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> Max35Text('').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^.{1,35}$"


class Max70Text(SEPAType):
    """
    >>> Max70Text('1' * 70).valid()
    True
    >>> Max70Text('1' * 71).valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> Max70Text('').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^.{1,70}$"


class RestrictedIdentificationSEPA1(SEPAType):
    """
    >>> RestrictedIdentificationSEPA1('Identifier-1. ').valid()
    True
    >>> RestrictedIdentificationSEPA1('A' * 35).valid()
    True
    >>> RestrictedIdentificationSEPA1('A' * 36).valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^([A-Za-z0-9]|[\+|\?|/|\-|:|\(|\)|\.|,|\'| ]){1,35}$"


class RestrictedIdentificationSEPA2(SEPAType):
    """
    >>> RestrictedIdentificationSEPA2('Identifier-2.').valid()
    True
    >>> RestrictedIdentificationSEPA2('A' * 35).valid()
    True
    >>> RestrictedIdentificationSEPA2('A' * 36).valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> RestrictedIdentificationSEPA2('with whitespace').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^([A-Za-z0-9]|[\+|\?|/|\-|:|\(|\)|\.|,|\']){1,35}$"


class RestrictedPersonIdentifierSEPA(SEPAType):
    """
    >>> RestrictedPersonIdentifierSEPA('DE71ZZZ00000111111').valid()
    True
    >>> RestrictedPersonIdentifierSEPA('Invalid').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = (
        r"^[a-zA-Z]{2,2}[0-9]{2,2}([A-Za-z0-9]|[\+|\?|/|\-|:|\(|\)|\.|,|\']){3,3}"  # noqa
        r"([A-Za-z0-9]|[\+|\?|/|\-|:|\(|\)|\.|,|\']){1,28}$"
    )


class ExternalLocalInstrument1Code(SEPAType):
    """
    >>> ExternalLocalInstrument1Code('COR1').valid()
    True
    >>> ExternalLocalInstrument1Code('Invalid').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^(CORE|COR1|B2B)$"


class ExternalCategoryPurpose1Code(SEPAType):
    """
    >>> ExternalCategoryPurpose1Code('CASH').valid()
    True
    >>> ExternalCategoryPurpose1Code('Invalid').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = (
        r"^(BONU|CASH|CBLK|CCRD|CORT|DCRD|DIVI|EPAY|FCOL|GOVT|HEDG|ICCP|IDCP|INTC|INTE|LOAN|OTHR|PENS|SALA|SECU|"  # noqa
        r"|SSBE|SUPP|TAXS|TRAD|TREA|VATX|WHLD)$"
    )


class ExternalPurpose1Code(SEPAType):
    """
    >>> ExternalPurpose1Code('CASH').valid()
    True
    >>> ExternalPurpose1Code('Invalid').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = (
        r"^(CBLK|CDCB|CDCD|CDCS|CDDP|CDOC|CDQC|ETUP|FCOL|MTUP|ACCT|CASH|COLL|CSDB|DEPT|INTC|LIMA|NETT|AGRT|AREN|"  # noqa
        r"BEXP|BOCE|COMC|CPYR|GDDS|GDSV|GSCB|LICF|POPE|ROYA|SCVE|SUBS|SUPP|TRAD|CHAR|COMT|CLPR|DBTC|GOVI|HLRP|"  # noqa
        r"INPC|INSU|INTE|LBRI|LIFI|LOAN|LOAR|PENO|PPTI|RINP|TRFD|ADMG|ADVA|BLDM|CBFF|CCRD|CDBL|CFEE|COST|CPKC|"  # noqa
        r"DCRD|EDUC|FAND|FCPM|GOVT|ICCP|IDCP|IHRP|INSM|IVPT|MSVC|NOWS|OFEE|OTHR|PADD|PTSP|RCKE|RCPT|REBT|REFU|"  # noqa
        r"RENT|STDY|TBIL|TCSC|TELI|WEBI|ANNI|CAFI|CFDI|CMDT|DERI|DIVD|FREX|HEDG|INVS|PRME|SAVG|SECU|SEPI|TREA|"  # noqa
        r"ANTS|CVCF|DMEQ|DNTS|HLTC|HLTI|HSPC|ICRF|LTCF|MDCS|VIEW|ALLW|ALMY|BBSC|BECH|BENE|BONU|COMM|CSLP|GVEA|"  # noqa
        r"GVEB|GVEC|GVED|PAYR|PENS|PRCP|SALA|SSBE|AEMP|GFRP|GWLT|RHBS|ESTX|FWLV|GSTX|HSTX|INTX|NITX|PTXP|RDTX|"  # noqa
        r"TAXS|VATX|WHLD|TAXR|AIRB|BUSB|FERB|RLWY|TRPT|CBTV|ELEC|ENRG|GASB|NWCH|NWCM|OTLC|PHON|UBIL|WTER)$"  # noqa
    )


class SequenceType1Code(SEPAType):
    """
    >>> SequenceType1Code('FNAL').valid()
    True
    >>> SequenceType1Code('Invalid').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^(FRST|RCUR|OOFF|FNAL)$"


class ISODate(SEPAType):
    """
    >>> ISODate('2000-01-01').valid()
    True
    >>> ISODate('20000101').valid()
    True
    >>> ISODate('2000-50-01').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
     >>> ISODate(date(2000, 1, 1)).value  # Date instances are fine.
     '2000-01-01'
    """

    syntax = r"^([0-9]{4})-?(1[0-2]|0[1-9])-?(3[0-1]|0[1-9]|[1-2][0-9])$"

    @staticmethod
    def transform(input_value):
        if hasattr(input_value, "isoformat"):
            return input_value.isoformat()
        return SEPAType.transform(input_value)


class ISODateTime(SEPAType):
    """
    >>> ISODateTime('2000-01-01T12:00:00Z').valid()
    True
    >>> ISODateTime('2000-01-01T12:00:00+01:00').valid()
    True
    >>> ISODateTime('2000-01-01T12:00:00').valid()
    True
    >>> ISODateTime('2000-01-01').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> ISODateTime(datetime(2000, 1, 1, 12, 0, 0)).value
    '2000-01-01T12:00:00'
    """

    syntax = (
        r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[0-1]|0[1-9]|[1-2][0-9])?"  # noqa
        r"T(2[0-3]|[0-1][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)??(Z|[+-](?:2[0-3]|[0-1][0-9]):[0-5][0-9])?$"  # noqa
    )

    @staticmethod
    def transform(input_value):
        if hasattr(input_value, "isoformat"):
            return input_value.isoformat()
        return SEPAType.transform(input_value)


class DecimalNumber(SEPAType):
    """
    >>> DecimalNumber('1').valid()
    True
    >>> DecimalNumber('{}.{}'.format('1' * 18, '1' * 17)).valid()
    True
    >>> DecimalNumber('1' * 19).valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    >>> DecimalNumber('1.001').value  # Numbers are truncated to two decimals.
    '1.00'
    """

    syntax = r"^\d{1,18}(\.\d{1,17})?$"

    @staticmethod
    def transform(input_value):
        return "{:.2f}".format(Decimal(input_value))


class BoolString(SEPAType):
    """
    >>> BoolString('true').valid()
    True
    >>> BoolString('invalid').valid()
    Traceback (most recent call last):
    pypain.exceptions.InvalidXMLValueException: ...
    """

    syntax = r"^(false|true)$"

    @staticmethod
    def transform(input_value):
        return str(input_value).lower()


class NullElementMaker(ElementMaker):

    def __call__(self, *args, **kwargs):
        filtered_args = [arg for arg in args if arg is not None]
        return ElementMaker.__call__(self, *filtered_args, **kwargs)


E = NullElementMaker(
    typemap={SEPAType: SEPAType.to_string},
    nsmap={
        None: "urn:iso:std:iso:20022:tech:xsd:pain.008.003.02",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    },
)

D = NullElementMaker(
    typemap={SEPAType: SEPAType.to_string},
    nsmap={
        None: "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    },
)


class XMLProducer:
    """Models a data class that is able to render to an XML representation."""

    xml_schema_path = None

    def to_xml(self):
        """Return lxml tree structure."""
        raise NotImplementedError(
            "Implement method `to_xml` to generate XML structure."
        )

    def valid(self):
        try:
            self.to_xml()
        except InvalidXMLValueException:
            return False
        return True


class SEPAMessage(XMLProducer):

    xml_schema_path = None

    """Models a data class that is able to render to an XML representation."""

    def to_string(self, validate_xml=True):
        """Return rendered XML as string."""
        xml_string = tostring(
            self.to_xml(), xml_declaration=False, encoding="unicode"
        )
        if validate_xml:
            if not self.valid_xml(xml_string):
                raise InvalidXMLException
        return xml_string

    def to_file(self, file, validate_xml=True):
        """Write rendered XML to file-like object `file`."""
        xml_string = tostring(
            self.to_xml(), xml_declaration=False, encoding="unicode"
        )
        if validate_xml:
            if not self.valid_xml(xml_string):
                raise InvalidXMLException
        file.write(xml_string)

    def valid_xml(self, xml_string):
        """Return True if `xml_string` conforms to SEPA XML schema."""
        if self.xml_schema_path is None:
            raise NotImplementedError(
                "XSD validation failed: path to schema is not set."
            )
        parsed_xml = parse(StringIO(xml_string))
        xsd_scheme = XMLSchema(parse(self.xml_schema_path))
        return xsd_scheme.validate(parsed_xml)


class Creditor:
    """Data collection of creditor information in a direct debit."""

    def __init__(self, name, iban, bic, ci, currency=None, ultimate_name=None):
        self.name = name
        self.iban = iban
        self.bic = bic
        self.ci = ci
        self.currency = currency
        self.ultimate_name = ultimate_name

    def __str__(self):
        return "Creditor <{}>".format(self.name)


class Debitor:
    """Data collection of debitor information in a bank wire."""

    def __init__(self, name, iban, bic, currency=None, ultimate_name=None):
        self.name = name
        self.iban = iban
        self.bic = bic
        self.currency = currency
        self.ultimate_name = ultimate_name

    def __str__(self):
        return "Debitor <{}>".format(self.name)


class Transaction(XMLProducer):

    def __init__(
        self,
        debtor_name,
        debtor_iban,
        debtor_bic,
        amount,
        purpose,
        mandate_id,
        mandate_date,
        reason,
        end_to_end_id=None,
        currency="EUR",
        ultimate_name=None,
        old_mandate_id=None,
        old_creditor_name=None,
        old_creditor_id=None,
        old_debtor_iban=None,
        new_debtor_agent=False,
    ):
        self._debtor_name = debtor_name
        self._debtor_iban = debtor_iban
        self._debtor_bic = debtor_bic
        self.amount = amount
        self._purpose = purpose
        self._mandate_id = mandate_id
        self._mandate_date = mandate_date
        self._mandate_changed = (
            old_mandate_id is not None or
            old_creditor_name is not None or
            old_creditor_id is not None or
            old_debtor_iban is not None or
            new_debtor_agent
        )
        self._reason = reason
        self._end_to_end_id = end_to_end_id
        self._currency = currency
        self._ultimate_name = ultimate_name
        self._old_mandate_id = old_mandate_id
        self._old_creditor_name = old_creditor_name
        self._old_creditor_id = old_creditor_id
        self._old_debtor_iban = old_debtor_iban
        self._new_debtor_agent = new_debtor_agent

    def to_xml(self):
        """Return lxml tree structure."""
        # Individual transaction
        root = E.DrctDbtTxInf(
            # Reference a single payment instruction
            E.PmtId(
                # Unambiguous reference of the submitter of a direct debit.
                E.EndToEndId(
                    RestrictedIdentificationSEPA1(self._end_to_end_id)
                    if self._end_to_end_id is not None
                    else "NOTPROVIDED"
                )
            ),
            # Amount of money to be moved
            E.InstdAmt(
                ActiveOrHistoricCurrencyAndAmountSEPA(self.amount),
                Ccy=self._currency,
            ),
            # Information specific to the direct debit mandate
            E.DrctDbtTx(
                # Further mandate information
                E.MndtRltdInf(
                    E.MndtId(RestrictedIdentificationSEPA2(self._mandate_id)),
                    # Date on which the mandate was signed
                    E.DtOfSgntr(ISODate(self._mandate_date)),
                    *[
                        # Signifier of a mandate change
                        E.AmdmntInd("true"),
                        # Further mandate change information
                        E.AmdmntInfDtls(
                            # Original mandate reference
                            E.OrgnlMndtId(
                                RestrictedIdentificationSEPA2(
                                    self._old_mandate_id
                                )
                            )
                            if self._old_mandate_id is not None
                            else None,
                            # Original creditor scheme information
                            E.OrgnlCdtrSchmeId(
                                # Name of former creditor
                                E.Nm(Max70Text(self._old_creditor_name))
                                if self._old_creditor_name is not None
                                else None,
                                *[
                                    # Identification of an individual
                                    E.Id(
                                        E.PrvtId(
                                            # Other unambiguous identifier
                                            E.Othr(
                                                # Original CI of creditor
                                                E.Id(
                                                    RestrictedPersonIdentifierSEPA(  # noqa
                                                        self._old_creditor_id
                                                    )
                                                ),
                                                E.SchmeNm(
                                                    # Name in text
                                                    E.Prtry("SEPA")
                                                ),
                                            )
                                        )
                                    )
                                ]
                                if self._old_creditor_id is not None
                                else []
                            )
                            if self._old_creditor_name is not None or
                                self._old_creditor_id is not None
                            else None,
                            # Original debtor account
                            E.OrgnlDbtrAcct(
                                # Identification of account
                                E.Id(
                                    # International Bank Account Number (IBAN)
                                    E.IBAN(
                                        IBAN2007Identifier(
                                            self._old_debtor_iban
                                        )
                                    )
                                )
                            )
                            if self._old_debtor_iban is not None
                            else None,
                            # Original debtor's agent
                            E.OrgnlDbtrAgt(
                                # Identification of debtor's agent
                                E.FinInstnId(
                                    E.Othr(
                                        E.Id(
                                            "SMNDA"
                                        )  # Same Mandate, New Debtor Agent
                                    )
                                )
                            )
                            if self._new_debtor_agent
                            else None,
                        ),
                    ]
                    if self._mandate_changed
                    else []
                )
            ),
            # Financial institution of debtor
            E.DbtrAgt(
                # Unique identification of institution
                E.FinInstnId(
                    # Business Identifier Code (SWIFT-Code)
                    E.BIC(BICIdentifier(self._debtor_bic))
                    if self._debtor_bic is not None
                    else None,
                    # Other identification of financial institutions
                    E.Othr(E.Id("NOTPROVIDED"))
                    if self._debtor_bic is None
                    else None,
                )
            ),
            # Information about the debtor
            E.Dbtr(
                # Name
                E.Nm(Max70Text(self._debtor_name))
            ),
            # Bank account of debtor
            E.DbtrAcct(
                # Identification of debtor's bank account
                E.Id(
                    # International Bank Account Number (IBAN)
                    E.IBAN(IBAN2007Identifier(self._debtor_iban))
                )
            ),
            # Debtor, if not bank account owner himself
            E.UltmtDbtr(
                # Name
                E.Nm(Max70Text(self._ultimate_name))
            )
            if self._ultimate_name is not None
            else None,
            # Type of payment
            E.Purp(
                # Type in coded format
                E.Cd(ExternalPurpose1Code(self._purpose))
            )
            if self._purpose is not None
            else None,
            # Remittance information
            E.RmtInf(
                # Unstructured information
                E.Ustrd(Max140Text(self._reason))
            )
            if self._reason is not None
            else None,
        )
        return root

    def __str__(self):
        return "Transaction <{amount} from {name}>".format(
            amount=self.amount, name=self._debtor_name
        )


class Payment(XMLProducer):
    """
    """

    def __init__(
        self,
        creditor,
        payment_id,
        direct_debit_type,
        sequence_type,
        purpose,
        payment_date,
        batch_booking=True,
    ):
        self._creditor = creditor
        self._payment_id = payment_id
        self._direct_debit_type = direct_debit_type
        self._sequence_type = sequence_type
        self._purpose = purpose
        self._payment_date = payment_date
        self._batch_booking = batch_booking
        self._transactions = []

    def add_transaction(
        self,
        debtor_name,
        debtor_iban,
        debtor_bic,
        amount,
        purpose,
        mandate_id,
        mandate_date,
        reason,
        end_to_end_id=None,
        currency="EUR",
        ultimate_name=None,
        old_mandate_id=None,
        old_creditor_name=None,
        old_creditor_id=None,
        old_debtor_iban=None,
        new_debtor_agent=False,
    ):
        transaction = Transaction(
            debtor_name=debtor_name,
            debtor_iban=debtor_iban,
            debtor_bic=debtor_bic,
            amount=amount,
            purpose=purpose,
            mandate_id=mandate_id,
            mandate_date=mandate_date,
            reason=reason,
            end_to_end_id=end_to_end_id,
            currency=currency,
            ultimate_name=ultimate_name,
            old_mandate_id=old_mandate_id,
            old_creditor_name=old_creditor_name,
            old_creditor_id=old_creditor_id,
            old_debtor_iban=old_debtor_iban,
            new_debtor_agent=new_debtor_agent,
        )
        self._transactions.append(transaction)
        return transaction

    def count_transactions(self):
        """Return number of associated transactions."""
        return len(self._transactions)

    def transactions_sum(self):
        """Returns sum of all transaction amounts in this payment."""
        return sum(transaction.amount for transaction in self._transactions)

    def to_xml(self):
        """Return lxml tree structure."""
        root = E.PmtInf(
            # Unique reference assigned to payment
            E.PmtInfId(RestrictedIdentificationSEPA1(self._payment_id)),
            # Means of payment, here: Direct Debit
            E.PmtMtd("DD"),
            E.BtchBookg(BoolString(self._batch_booking)),
            # Number of included transactions
            E.NbOfTxs(Max15NumericText(len(self._transactions))),
            # Sum of all included transactions with two decimal places
            E.CtrlSum(DecimalNumber(self.transactions_sum())),
            # Type of transaction
            E.PmtTpInf(
                # Agreement under which the transactions should be processed
                E.SvcLvl(
                    # In coded format
                    E.Cd("SEPA")
                ),
                # Type of direct debit
                E.LclInstrm(
                    # In coded format
                    E.Cd(ExternalLocalInstrument1Code(self._direct_debit_type))
                ),
                E.SeqTp(SequenceType1Code(self._sequence_type)),
                # Type of payment
                E.CtgyPurp(
                    # In coded format
                    E.Cd(ExternalCategoryPurpose1Code(self._purpose))
                )
                if self._purpose is not None
                else None,
            ),
            # Requested collection date
            E.ReqdColltnDt(ISODate(self._payment_date)),
            # Creditor Information
            E.Cdtr(
                # Name
                E.Nm(Max70Text(self._creditor.name))
            ),
            # Bank account of creditor
            E.CdtrAcct(
                # Identification of bank account
                E.Id(
                    # International Bank Account Number (IBAN)
                    E.IBAN(IBAN2007Identifier(self._creditor.iban))
                ),
                # Currency of bank account
                E.Ccy(ActiveOrHistoricCurrencyCode(self._creditor.currency))
                if self._creditor.currency is not None
                else None,
            ),
            # Financial institution of creditor
            E.CdtrAgt(
                # Identification of the institution
                E.FinInstnId(
                    # Business Identifier Code (SWIFT-Code)
                    E.BIC(BICIdentifier(self._creditor.bic))
                    if self._creditor.bic is not None
                    else None,
                    # Other means of identification
                    E.Othr(E.Id("NOTPROVIDED"))
                    if self._creditor.bic is None
                    else None,
                )
            ),
            # Name of ultimate creditor, if not the creditor above.
            E.UltmtCdtr(
                # Name
                E.Nm(Max70Text(self._creditor.ultimate_name))
            )
            if self._creditor.ultimate_name is not None
            else None,
            E.ChrgBr("SLEV"),  # Both parties bear their own charges
            # Credit party that signs the mandate
            E.CdtrSchmeId(
                # Identification of an organisation or person
                E.Id(
                    # Unique identification of a person
                    E.PrvtId(
                        # Other types of identification
                        E.Othr(
                            # Creditor Identification (CI)
                            E.Id(
                                RestrictedPersonIdentifierSEPA(
                                    self._creditor.ci
                                )
                            ),
                            # Name of identification scheme
                            E.SchmeNm(
                                # Name in free text
                                E.Prtry("SEPA")
                            ),
                        )
                    )
                )
            ),
            *[transaction.to_xml() for transaction in self._transactions]
        )
        return root

    def __iter__(self):
        """Iterate over transactions."""
        yield from self._transactions

    def __getitem__(self, key):
        """Access transaction via index."""
        return self._transactions[key]

    def __str__(self):
        return "Payment <{}>".format(self._payment_id)


class CreditTransaction(XMLProducer):

    def __init__(
        self,
        creditor_name,
        creditor_iban,
        creditor_bic,
        amount,
        reason,
        currency="EUR",
    ):
        self._creditor_name = creditor_name
        self._creditor_iban = creditor_iban
        self._creditor_bic = creditor_bic
        self.amount = amount
        self._reason = reason
        self._currency = currency
        self._end_to_end_id = None

    def to_xml(self):
        """Return lxml tree structure."""
        # Individual transaction
        root = D.CdtTrfTxInf(
            # Reference a single payment instruction
            D.PmtId(
                # Unambiguous reference of the submitter of a direct debit.
                D.EndToEndId(
                    RestrictedIdentificationSEPA1(self._end_to_end_id)
                    if self._end_to_end_id is not None
                    else "NOTPROVIDED"
                )
            ),
            # Amount of money to be moved
            D.Amt(
                D.InstdAmt(
                    ActiveOrHistoricCurrencyAndAmountSEPA(self.amount),
                    Ccy=self._currency,
                )
            ),
            # Information about the debtor
            D.Cdtr(
                # Name
                D.Nm(Max70Text(self._creditor_name))
            ),
            # Bank account of debtor
            D.CdtrAcct(
                # Identification of debtor's bank account
                D.Id(
                    # International Bank Account Number (IBAN)
                    D.IBAN(IBAN2007Identifier(self._creditor_iban))
                )
            ),
            # Remittance information
            D.RmtInf(
                # Unstructured information
                D.Ustrd(Max140Text(self._reason))
            )
            if self._reason is not None
            else None,
        )
        return root

    def __str__(self):
        return "Credit Transaction <{amount} from {name}>".format(
            amount=self.amount, name=self._creditor_name
        )


class Transfer(XMLProducer):
    """
    """

    def __init__(
        self,
        debitor,
        payment_id,
        payment_date,
    ):
        self._debitor = debitor
        self._payment_id = payment_id
        self._payment_date = payment_date
        self._transactions = []

    def add_transaction(
        self,
        creditor_name,
        creditor_iban,
        creditor_bic,
        amount,
        reason,
        currency="EUR",
    ):
        transaction = CreditTransaction(
            creditor_name=creditor_name,
            creditor_iban=creditor_iban,
            creditor_bic=creditor_bic,
            amount=amount,
            reason=reason,
            currency=currency,
        )
        self._transactions.append(transaction)
        return transaction

    def count_transactions(self):
        """Return number of associated transactions."""
        return len(self._transactions)

    def transactions_sum(self):
        """Returns sum of all transaction amounts in this payment."""
        return sum(transaction.amount for transaction in self._transactions)

    def to_xml(self):
        """Return lxml tree structure."""
        root = D.PmtInf(
            # Unique reference assigned to payment
            D.PmtInfId(RestrictedIdentificationSEPA1(self._payment_id)),
            # Means of payment, here: Direct Debit
            D.PmtMtd("TRF"),
            # Number of included transactions
            D.NbOfTxs(Max15NumericText(len(self._transactions))),
            # Sum of all included transactions with two decimal places
            D.CtrlSum(DecimalNumber(self.transactions_sum())),
            # Requested collection date
            D.ReqdExctnDt(ISODate(self._payment_date)),
            D.Dbtr(
                # Name
                D.Nm(Max70Text(self._debitor.name))
            ),
            # Bank account of creditor
            D.DbtrAcct(
                # Identification of bank account
                D.Id(
                    # International Bank Account Number (IBAN)
                    D.IBAN(IBAN2007Identifier(self._debitor.iban))
                ),
                # Currency of bank account
                D.Ccy(ActiveOrHistoricCurrencyCode(self._debitor.currency))
                if self._debitor.currency is not None
                else None,
            ),
            # Financial institution of creditor
            D.DbtrAgt(
                # Identification of the institution
                D.FinInstnId(
                    # Business Identifier Code (SWIFT-Code)
                    D.BIC(BICIdentifier(self._debitor.bic))
                    if self._debitor.bic is not None
                    else None,
                    # Other means of identification
                    D.Othr(E.Id("NOTPROVIDED"))
                    if self._debitor.bic is None
                    else None,
                )
            ),
            # Name of ultimate creditor, if not the creditor above.
            D.UltmtCdtr(
                # Name
                D.Nm(Max70Text(self._debitor.ultimate_name))
            )
            if self._debitor.ultimate_name is not None
            else None,
            D.ChrgBr("SLEV"),  # Both parties bear their own charges
            # Credit party that signs the mandate
            *[transaction.to_xml() for transaction in self._transactions]
        )
        return root

    def __iter__(self):
        """Iterate over transactions."""
        yield from self._transactions

    def __getitem__(self, key):
        """Access transaction via index."""
        return self._transactions[key]

    def __str__(self):
        return "Transfer <{}>".format(self._payment_id)


class BankWire(SEPAMessage):
    """SEPA bank wire message, containing payments and transactions."""

    xml_schema_path = str(
        Path(__file__).absolute().parent / "pain.001.001.03.xsd"
    )

    def __init__(
        self,
        message_id,
        debitor_name,
        debitor_iban,
        debitor_bic,
        debitor_currency=None,
        debitor_ultimate_name=None,
    ):
        self.message_id = message_id
        self._debitor = Debitor(
            name=debitor_name,
            iban=debitor_iban,
            bic=debitor_bic,
            currency=debitor_currency,
            ultimate_name=debitor_ultimate_name,
        )
        self._transfers = []

    def add_transfer(
        self,
        payment_id,
        payment_date,
        batch_booking=True,
    ):
        transfer = Transfer(
            debitor=self._debitor,
            payment_id=payment_id,
            payment_date=payment_date,
        )
        self._transfers.append(transfer)
        return transfer

    def count_transfers(self):
        return len(self._transfers)

    def transactions_sum(self):
        return sum(
            [transfer.transactions_sum() for transfer in self._transfers]
        )

    def count_transactions(self):
        """Return number of all transaction of this bank transfer."""
        return sum(
            [transfer.count_transactions() for transfer in self._transfers]
        )

    def to_xml(self, check_xsd=False):
        """Return lxml tree structure."""
        root = D.Document(
            # Customer Credit Transfer Initiation
            D.CstmrCdtTrfInitn(
                # Characteristics shared by all transactions in this message
                D.GrpHdr(
                    # End-to-end reference of this message
                    D.MsgId(RestrictedIdentificationSEPA1(self.message_id)),
                    # Date and time of file generation
                    D.CreDtTm(ISODateTime(datetime.now().isoformat())),
                    # Number of individual transaction in this file
                    D.NbOfTxs(Max15NumericText(self.count_transactions())),
                    D.CtrlSum(DecimalNumber(self.transactions_sum())),
                    # Initiating party
                    D.InitgPty(
                        # Name
                        D.Nm(Max70Text(self._debitor.name))
                    ),
                ),
                *[transfer.to_xml() for transfer in self._transfers]
            ),
            **{
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": (
                    "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03 "
                    "pain.001.001.03.xsd")
            }
        )
        return root

    def __iter__(self):
        """Iterate over assigned payments."""
        yield from self._transfers

    def __getitem__(self, key):
        """Access payments via index. """
        return self._transfers[key]

    def __str__(self):
        return " <{}>".format(self.message_id)


class DirectDebit(SEPAMessage):
    """SEPA Direct Debit message, containing payments and transactions."""

    xml_schema_path = str(
        Path(__file__).absolute().parent / "pain.008.003.02.xsd"
    )

    def __init__(
        self,
        message_id,
        creditor_name,
        creditor_ci,
        creditor_iban,
        creditor_bic=None,
        creditor_currency=None,
        creditor_ultimate_name=None,
    ):
        """
        Initialize a SEPA direct debit process.
        :param message_id: unique, point-to-point reference for this process
        :param creditor_name: name of creditor
        :param creditor_ci: Creditor Identifier (CI)
        :param creditor_iban: creditor's bank account IBAN
        :param creditor_bic: creditor's bank account BIC
        :param creditor_currency: creditor's bank account currency
        :param creditor_ultimate_name: creditor reference party
        """
        self.message_id = message_id
        self._creditor = Creditor(
            name=creditor_name,
            iban=creditor_iban,
            bic=creditor_bic,
            ci=creditor_ci,
            currency=creditor_currency,
            ultimate_name=creditor_ultimate_name,
        )
        self._payments = []

    def add_payment(
        self,
        payment_id,
        direct_debit_type,
        sequence_type,
        purpose,
        payment_date,
        batch_booking=True,
    ):
        payment = Payment(
            creditor=self._creditor,
            payment_id=payment_id,
            direct_debit_type=direct_debit_type,
            sequence_type=sequence_type,
            purpose=purpose,
            payment_date=payment_date,
            batch_booking=batch_booking,
        )
        self._payments.append(payment)
        return payment

    def count_payments(self):
        """Return number of assigned payments."""
        return len(self._payments)

    def transactions_sum(self):
        return sum([payment.transactions_sum() for payment in self._payments])

    def count_transactions(self):
        """Return number of all transaction of this Direct Debit."""
        return sum(
            [payment.count_transactions() for payment in self._payments]
        )

    def to_xml(self, check_xsd=False):
        """Return lxml tree structure."""
        root = E.Document(
            # Customer Direct Debit Initiation
            E.CstmrDrctDbtInitn(
                # Characteristics shared by all transactions in this message
                E.GrpHdr(
                    # End-to-end reference of this message
                    E.MsgId(RestrictedIdentificationSEPA1(self.message_id)),
                    # Date and time of file generation
                    E.CreDtTm(ISODateTime(datetime.now().isoformat())),
                    # Number of individual transaction in this file
                    E.NbOfTxs(Max15NumericText(self.count_transactions())),
                    E.CtrlSum(DecimalNumber(self.transactions_sum())),
                    # Initiating party
                    E.InitgPty(
                        # Name
                        E.Nm(Max70Text(self._creditor.name))
                    ),
                ),
                *[payment.to_xml() for payment in self._payments]
            ),
            **{
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": (
                    "urn:iso:std:iso:20022:tech:xsd:pain.008.003.02 "
                    "pain.008.003.02.xsd")
            }
        )
        return root

    def __iter__(self):
        """Iterate over assigned payments."""
        yield from self._payments

    def __getitem__(self, key):
        """Access payments via index. """
        return self._payments[key]

    def __str__(self):
        return "Direct Debit <{}>".format(self.message_id)
