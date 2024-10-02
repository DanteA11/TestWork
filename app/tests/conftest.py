import asyncio
import os

import pytest

os.environ["DATABASE_URL"] = "postgresql+psycopg_async://admin:admin@localhost/tests"

import models


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
def create_and_drop_tables():
    asyncio.run(models.start_conn(True))
    yield
    asyncio.run(models.stop_conn())


@pytest.fixture(scope="module")
async def create_and_drop_tables_async():
    await models.start_conn(True)
    yield
    await models.stop_conn()
