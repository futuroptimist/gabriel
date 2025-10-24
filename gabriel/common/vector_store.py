"""Secure vector store utilities with repository-scoped API key enforcement."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Callable, Mapping, Sequence
from uuid import uuid4

MAX_VECTOR_TTL = timedelta(days=7)


@dataclass(frozen=True, slots=True)
class VectorRecord:
    """Represents an embedding stored in the vector store."""

    identifier: str
    embedding: tuple[float, ...]
    metadata: Mapping[str, str]
    api_key_id: str
    expires_at: datetime

    def is_expired(self, *, reference: datetime | None = None) -> bool:
        """Return ``True`` when the record has expired relative to ``reference``."""

        check_time = reference or datetime.now(tz=timezone.utc)
        return check_time >= self.expires_at


class SecureVectorStore:
    """In-memory vector store enforcing repository-scoped API keys and TTLs."""

    def __init__(self, repository: str, *, now: Callable[[], datetime] | None = None) -> None:
        if not repository or not repository.strip():
            raise ValueError("repository must be a non-empty string")
        self._repository = repository.strip()
        self._records: dict[str, VectorRecord] = {}
        self._now = now or (lambda: datetime.now(tz=timezone.utc))

    @property
    def repository(self) -> str:
        """Return the repository scope enforced by the store."""

        return self._repository

    def write_embedding(
        self,
        embedding: Sequence[float],
        *,
        api_key_id: str,
        ttl: timedelta | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> VectorRecord:
        """Persist ``embedding`` with repository-scoped API key enforcement."""

        normalized_key = self._validate_api_key(api_key_id)
        normalized_ttl = self._validate_ttl(ttl)
        embedding_tuple = self._normalize_embedding(embedding)
        metadata_map = self._normalize_metadata(metadata)
        identifier = str(uuid4())
        expires_at = self._now() + normalized_ttl
        record = VectorRecord(
            identifier=identifier,
            embedding=embedding_tuple,
            metadata=metadata_map,
            api_key_id=normalized_key,
            expires_at=expires_at,
        )
        self._records[identifier] = record
        return record

    def get(self, identifier: str, /) -> VectorRecord | None:
        """Return the stored record identified by ``identifier``."""

        return self._records.get(identifier)

    def active_records(self) -> tuple[VectorRecord, ...]:
        """Return all non-expired records in insertion order."""

        now = self._now()
        return tuple(record for record in self._records.values() if not record.is_expired(reference=now))

    def purge_expired(self) -> int:
        """Remove expired records and return the number of purged items."""

        now = self._now()
        expired = [key for key, record in self._records.items() if record.is_expired(reference=now)]
        for key in expired:
            del self._records[key]
        return len(expired)

    def __len__(self) -> int:  # pragma: no cover - simple delegation
        return len(self._records)

    def _validate_api_key(self, api_key_id: str) -> str:
        if not api_key_id or not api_key_id.strip():
            raise ValueError("api_key_id must be a non-empty string")
        api_key_id = api_key_id.strip()
        expected_prefix = f"{self._repository}:"
        if not api_key_id.startswith(expected_prefix):
            raise ValueError(
                "api_key_id must be scoped to repository "
                f"'{self._repository}' using the '{expected_prefix}<suffix>' format"
            )
        return api_key_id

    def _validate_ttl(self, ttl: timedelta | None) -> timedelta:
        normalized = ttl if ttl is not None else MAX_VECTOR_TTL
        if normalized <= timedelta(0):
            raise ValueError("ttl must be greater than zero")
        if normalized > MAX_VECTOR_TTL:
            raise ValueError(
                f"ttl must be less than or equal to {MAX_VECTOR_TTL.days} days"
            )
        return normalized

    @staticmethod
    def _normalize_embedding(embedding: Sequence[float]) -> tuple[float, ...]:
        if not embedding:
            raise ValueError("embedding must include at least one value")
        normalized: list[float] = []
        for value in embedding:
            number = float(value)
            if not math.isfinite(number):
                raise ValueError("embedding values must be finite numbers")
            normalized.append(number)
        return tuple(normalized)

    @staticmethod
    def _normalize_metadata(metadata: Mapping[str, str] | None) -> Mapping[str, str]:
        if metadata is None:
            return MappingProxyType({})
        materialized: dict[str, str] = {}
        for key, value in metadata.items():
            key_str = str(key).strip()
            if not key_str:
                raise ValueError("metadata keys must be non-empty strings")
            materialized[key_str] = str(value)
        return MappingProxyType(materialized)


__all__ = ["MAX_VECTOR_TTL", "VectorRecord", "SecureVectorStore"]
