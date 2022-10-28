import os

from deta import Deta
from dotenv import load_dotenv

load_dotenv('.env')
DETA_KEY = os.getenv('DETA_KEY')

# INITIALIZE WITH PROJECT KEY
deta = Deta(DETA_KEY)

# CREATE/CONNECT TO DB
db = deta.Base("monthly_reports")

# Actions
def insert_period(period, incomes, expenses, comment):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db.put({'key': period, 'incomes': incomes, 'expenses': expenses, 'comment': comment})


def fetch_all_periods():
    """Returns a list of all periods"""
    res = db.fetch()
    return res.items


def get_period(period):
    """Returns the report for a given period, if not found it will return None"""
    res = db.get(period)
    return res
