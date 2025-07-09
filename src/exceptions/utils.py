from datetime import date

from fastapi import HTTPException


def check_data_from_after_date_to_http_exc(date_from: date, date_to: date):
    if date_from <= date_to:
        raise HTTPException(422, "date_from должно быть больше date_to")
