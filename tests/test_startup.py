
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.main import initialize_indexes


@pytest.mark.asyncio
async def test_initialize_indexes_creates_unique_checksum_index(
    monkeypatch,
):
    collection = MagicMock()
    collection.create_index = AsyncMock(
        return_value="checksum_1"
    )

    client = MagicMock()
    client.__getitem__.return_value.__getitem__.return_value = (
        collection
    )
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr(
        "app.main.AsyncMongoClient",
        lambda uri: client,
    )

    await initialize_indexes()

    collection.create_index.assert_awaited_once_with(
        "checksum",
        unique=True,
    )
