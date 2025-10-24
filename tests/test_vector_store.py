from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from gabriel.common.vector_store import MAX_VECTOR_TTL, SecureVectorStore


class _Clock:
    def __init__(self, start: datetime) -> None:
        self._current = start

    def now(self) -> datetime:
        return self._current

    def advance(self, delta: timedelta) -> None:
        self._current += delta


@pytest.fixture()
def clock() -> _Clock:
    return _Clock(datetime(2024, 1, 1, tzinfo=timezone.utc))


def test_write_embedding_requires_repo_scoped_api_key(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding([0.1, 0.2], api_key_id="other:123")


def test_store_requires_non_empty_repository() -> None:
    with pytest.raises(ValueError):
        SecureVectorStore(" ")


def test_repository_property_returns_scope(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    assert store.repository == "gabriel"


def test_write_embedding_rejects_excessive_ttl(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding(
            [0.1, 0.2],
            api_key_id="gabriel:token",
            ttl=MAX_VECTOR_TTL + timedelta(seconds=1),
        )


def test_write_embedding_rejects_non_positive_ttl(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding(
            [0.1],
            api_key_id="gabriel:token",
            ttl=timedelta(seconds=0),
        )


def test_write_embedding_defaults_to_maximum_ttl(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    record = store.write_embedding([0.1, 0.2], api_key_id="gabriel:key")

    assert record.expires_at - clock.now() == MAX_VECTOR_TTL


def test_purge_expired_removes_records(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    store.write_embedding([0.1], api_key_id="gabriel:key", ttl=timedelta(seconds=1))
    clock.advance(timedelta(seconds=2))

    purged = store.purge_expired()

    assert purged == 1
    assert store.active_records() == ()


def test_metadata_keys_must_be_non_empty(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding(
            [0.1],
            api_key_id="gabriel:key",
            metadata={"": "value"},
        )


def test_embedding_values_must_be_finite(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding([float("nan")], api_key_id="gabriel:key")


def test_write_embedding_rejects_blank_api_key(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding([0.1], api_key_id="  ")


def test_write_embedding_rejects_empty_embedding(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding([], api_key_id="gabriel:key")


def test_get_returns_record_by_identifier(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    record = store.write_embedding([0.1], api_key_id="gabriel:key")

    assert store.get(record.identifier) is record


def test_metadata_normalization_returns_immutable_mapping(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    record = store.write_embedding(
        [0.1],
        api_key_id="gabriel:key",
        metadata={"Task": "report", "priority": 1},
    )

    assert record.metadata["Task"] == "report"
    assert record.metadata["priority"] == "1"
    with pytest.raises(TypeError):
        record.metadata["added"] = "nope"  # type: ignore[index]
