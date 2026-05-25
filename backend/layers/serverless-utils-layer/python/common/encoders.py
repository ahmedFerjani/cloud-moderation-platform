import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):

    def default(self, o: object) -> object:

        if isinstance(o, Decimal):
            return float(o)

        return super().default(o)
