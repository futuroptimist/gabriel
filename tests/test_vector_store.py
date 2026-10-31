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
        store.write_embedding([0.1, 0.2], api_key_id="other:123", task_id="task-1")


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
            task_id="task-1",
            ttl=MAX_VECTOR_TTL + timedelta(seconds=1),
        )


def test_write_embedding_rejects_non_positive_ttl(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding(
            [0.1],
            api_key_id="gabriel:token",
            task_id="task-1",
            ttl=timedelta(seconds=0),
        )


def test_write_embedding_defaults_to_maximum_ttl(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    record = store.write_embedding([0.1, 0.2], api_key_id="gabriel:key", task_id="task-1")

    assert record.expires_at - clock.now() == MAX_VECTOR_TTL


def test_purge_expired_removes_records(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    store.write_embedding(
        [0.1],
        api_key_id="gabriel:key",
        task_id="task-1",
        ttl=timedelta(seconds=1),
    )
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
            task_id="task-1",
            metadata={"": "value"},
        )


def test_embedding_values_must_be_finite(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding([float("nan")], api_key_id="gabriel:key", task_id="task-1")


def test_write_embedding_rejects_blank_api_key(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding([0.1], api_key_id="  ", task_id="task-1")


def test_write_embedding_rejects_empty_embedding(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding([], api_key_id="gabriel:key", task_id="task-1")


def test_get_returns_record_by_identifier(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    record = store.write_embedding([0.1], api_key_id="gabriel:key", task_id="task-1")

    assert store.get(record.identifier) is record


def test_metadata_normalization_returns_immutable_mapping(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    record = store.write_embedding(
        [0.1],
        api_key_id="gabriel:key",
        task_id="task-1",
        metadata={"Task": "report", "priority": 1},
    )

    assert record.metadata["Task"] == "report"
    assert record.metadata["priority"] == "1"
    with pytest.raises(TypeError):
        record.metadata["added"] = "nope"  # type: ignore[index]


def test_write_embedding_requires_task_id(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.write_embedding([0.1], api_key_id="gabriel:key", task_id="   ")


def test_created_at_defaults_to_current_time(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    before = clock.now()
    record = store.write_embedding([0.1], api_key_id="gabriel:key", task_id="task-1")
    after = clock.now()

    assert before <= record.created_at <= after


def test_created_at_accepts_custom_timestamp(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    custom = datetime(2023, 12, 31, 23, tzinfo=timezone.utc)
    record = store.write_embedding(
        [0.2],
        api_key_id="gabriel:key",
        task_id="task-1",
        created_at=custom,
    )

    assert record.created_at == custom


def test_created_at_normalizes_naive_timestamp(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    naive = datetime(2023, 12, 31, 23)
    record = store.write_embedding(
        [0.25],
        api_key_id="gabriel:key",
        task_id="task-1",
        created_at=naive,
    )

    assert record.created_at.tzinfo is not None
    assert record.created_at.hour == naive.hour


def test_records_for_task_filters_results(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    first = store.write_embedding([0.1], api_key_id="gabriel:key", task_id="task-1")
    store.write_embedding([0.2], api_key_id="gabriel:key", task_id="task-2")

    records = store.records_for_task("task-1")

    assert records == (first,)


def test_purge_stale_removes_old_records(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)
    old_time = clock.now() - timedelta(hours=2)
    new_time = clock.now() - timedelta(minutes=5)
    old = store.write_embedding(
        [0.3],
        api_key_id="gabriel:key",
        task_id="task-1",
        created_at=old_time,
    )
    fresh = store.write_embedding(
        [0.4],
        api_key_id="gabriel:key",
        task_id="task-2",
        created_at=new_time,
    )

    purged = store.purge_stale(timedelta(hours=1))

    assert purged == 1
    assert store.get(old.identifier) is None
    assert store.get(fresh.identifier) is fresh


def test_purge_stale_rejects_non_positive_age(clock: _Clock) -> None:
    store = SecureVectorStore("gabriel", now=clock.now)

    with pytest.raises(ValueError):
        store.purge_stale(timedelta(seconds=0))
