import pytest
from sqlalchemy.orm import sessionmaker

from app.database import engine


@pytest.fixture()
def db_session():
    """One connection + one outer transaction per test, rolled back at
    teardown. `join_transaction_mode="create_savepoint"` lets application
    code call session.commit() (as our routers' dependency-injected session
    would in real use) without actually committing past the test boundary -
    commit() just closes/reopens a SAVEPOINT instead of the real
    transaction."""
    connection = engine.connect()
    outer_transaction = connection.begin()
    TestSession = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()
