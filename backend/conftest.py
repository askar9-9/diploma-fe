import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.init_db import init_db


@pytest.fixture(scope="function")
def engine():
    eng = create_engine("sqlite:///:memory:", echo=False)
    yield eng
    eng.dispose()


@pytest.fixture(scope="function")
def session(engine):
    init_db(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()
