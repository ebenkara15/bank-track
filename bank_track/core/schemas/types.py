from enum import StrEnum


class CurrencyType(StrEnum):
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    UNKNOWN = "UNKNOWN"
    XXX = "XXX"

    @staticmethod
    def default():
        return CurrencyType.EUR


class CashAccountType(StrEnum):
    CARD = "CARD"
    CURRENT = "CACC"
    CASH_PAYMENT = "CASH"
    CHARGES = "CHAR"
    CASH_INCOME = "CISH"
    COMMISSION = "COMM"
    CLEARING_PARTICIPANT_SETTLEMENT_ACCOUNT = "CPAC"
    LIMITED_LIQUIDITY_SAVINGS_ACCOUNT = "LLSV"
    LOAN = "LOAN"
    MARGINAL_LENDING = "MGLD"
    MONEY_MARKET = "MOMA"
    NON_RESIDENT_EXTERNAL = "NREX"
    OVERDRAFT = "ODFT"
    OVER_NIGHT_DEPOSIT = "ONDP"
    OTHER_ACCOUNT = "OTHR"
    SETTLEMENT = "SACC"
    SALARY = "SLRY"
    SAVINGS = "SVGS"
    TAX = "TAXE"
    TRANSACTING_ACCOUNT = "TRAN"

    @staticmethod
    def default():
        return CashAccountType.CARD


class BalanceType(StrEnum):
    EXPECTED = "expected"
    CLOSING_BOOKED = "closingBooked"
    INFORMATION = "information"
    INTERIM_AVAILABLE = "interimAvailable"
    AUTHORISED = "authorised"
    OPENING_BOOKED = "openingBooked"
    FORWARD_AVAILABLE = "forwardAvailable"
    NON_INVOICED = "nonInvoiced"
    AVAILABLE = "available"

    @staticmethod
    def default():
        return BalanceType.AVAILABLE
