"""Typed protocols that define Gabriel's cross-cutting service contracts."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Protocol


class KeyManager(Protocol):
    """Provide access to encryption key material."""

    def get_public_key(self, key_id: str, /) -> bytes:
        """Return the public key identified by ``key_id``."""

    def get_private_key(self, key_id: str, /) -> bytes:
        """Return the private key identified by ``key_id``."""


class EnvelopeEncryptor(Protocol):
    """Encrypt and decrypt payloads using envelope encryption."""

    def encrypt(self, plaintext: bytes, /, *, key_id: str | None = None) -> tuple[bytes, bytes]:
        """Return a tuple of ``(ciphertext, wrapped_key)`` for ``plaintext``."""

    def decrypt(self, ciphertext: bytes, wrapped_key: bytes, /) -> bytes:
        """Decrypt ``ciphertext`` using ``wrapped_key`` and return the plaintext."""


class SecretStore(Protocol):
    """Store, retrieve, and delete credential material."""

    def store(self, service: str, username: str, secret: str, /) -> None:
        """Persist ``secret`` for ``service``/``username``."""

    def retrieve(self, service: str, username: str, /) -> str | None:
        """Return the stored secret or ``None`` when it does not exist."""

    def delete(self, service: str, username: str, /) -> None:
        """Remove the stored secret if one exists."""


class KnowledgeRepository(Protocol):
    """Persist and query knowledge captured during ingestion."""

    def add_documents(self, documents: Iterable[str], /) -> None:
        """Index the provided ``documents`` for later retrieval."""

    def search(self, query: str, /, *, limit: int = 10) -> Sequence[str]:
        """Return a ranked sequence of documents matching ``query``."""


class InferenceClient(Protocol):
    """Provide access to LLM inference, either local or remote."""

    def complete(self, prompt: str, /, *, temperature: float = 0.0) -> str:
        """Generate a completion for ``prompt``."""

    def score(self, prompt: str, completion: str, /) -> float:
        """Return a model-specific score for ``completion`` given ``prompt``."""


__all__ = [
    "KeyManager",
    "EnvelopeEncryptor",
    "SecretStore",
    "KnowledgeRepository",
    "InferenceClient",
]
