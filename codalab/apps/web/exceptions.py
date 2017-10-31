from decimal import Decimal


class ScoringException(Exception):
    value = Decimal('0.0')
    score_def_id = None
    result_id = None
    pass
