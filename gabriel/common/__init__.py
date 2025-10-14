"""Shared service interfaces and registries used across Gabriel modules."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

__all__ = [
    "KeyManager",
    "EnvelopeEncryptor",
    "SecretStore",
    "KnowledgeRepository",
    "InferenceClient",
    "InferenceResult",
    "ServiceRegistry",
    "register_secret_store",
    "get_secret_store",
    "available_secret_stores",
    "register_knowledge_repository",
    "get_knowledge_repository",
    "available_knowledge_repositories",
    "register_inference_client",
    "get_inference_client",
    "available_inference_clients",
]


@runtime_checkable
class KeyManager(Protocol):
    """Protocol describing minimal key management capabilities."""

    def default_key_id(self) -> str:
        """Return the identifier of the key used for new encrypt operations."""

    def load_key(self, key_id: str) -> bytes:
        """Return the raw key material associated with ``key_id``."""

    def list_keys(self) -> Iterable[str]:
        """Yield known key identifiers for auditing and discovery."""


@runtime_checkable
class EnvelopeEncryptor(Protocol):
    """Protocol describing an encryptor that produces sealed payloads."""

    def encrypt(self, plaintext: bytes, *, key_id: str | None = None) -> tuple[str, bytes]:
        """Return a tuple of ``key_id`` and ciphertext for ``plaintext``."""

    def decrypt(self, ciphertext: bytes, *, key_id: str) -> bytes:
        """Return decrypted plaintext for ``ciphertext`` encrypted with ``key_id``."""


@runtime_checkable
class SecretStore(Protocol):
    """Protocol describing secret persistence helpers."""

    def store(self, service: str, username: str, secret: str) -> None:
        """Persist ``secret`` so it can be retrieved later."""

    def retrieve(self, service: str, username: str) -> str | None:
        """Return the previously stored secret if present."""

    def delete(self, service: str, username: str) -> None:
        """Remove stored secret material when no longer required."""


@runtime_checkable
class KnowledgeRepository(Protocol):
    """Protocol describing a searchable collection of knowledge notes."""

    def add(self, note: Any) -> None:
        """Persist ``note`` into the repository."""

    def search(
        self,
        query: str,
        *,
        required_tags: Iterable[str] | None = None,
        limit: int | None = None,
    ) -> list[Any]:
        """Return ranked search results for ``query``."""


@dataclass(frozen=True)
class InferenceResult:
    """Represents the outcome of an LLM inference request."""

    text: str
    model: str
    metadata: Mapping[str, Any]


@runtime_checkable
class InferenceClient(Protocol):
    """Protocol describing the minimum inference capabilities used by Gabriel."""

    def infer(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> InferenceResult:
        """Run inference for ``prompt`` and return a structured result."""


_T = TypeVar("_T")


class ServiceRegistry(Generic[_T]):
    """Typed registry that maps string keys to service factories."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[..., _T]] = {}

    def register(self, name: str, factory: Callable[..., _T]) -> None:
        """Register ``factory`` under ``name``."""

        if name in self._factories:
            raise ValueError(f"Service factory already registered for '{name}'")
        self._factories[name] = factory

    def create(self, name: str, *args: Any, **kwargs: Any) -> _T:
        """Instantiate the service registered as ``name``."""

        try:
            factory = self._factories[name]
        except KeyError as error:
            raise LookupError(f"No factory registered for '{name}'") from error
        return factory(*args, **kwargs)

    def available(self) -> tuple[str, ...]:
        """Return a tuple of registered factory names."""

        return tuple(sorted(self._factories))


_secret_store_registry: ServiceRegistry[SecretStore] = ServiceRegistry()
_knowledge_registry: ServiceRegistry[KnowledgeRepository] = ServiceRegistry()
_inference_registry: ServiceRegistry[InferenceClient] = ServiceRegistry()


def register_secret_store(name: str, factory: Callable[..., SecretStore]) -> None:
    """Register a ``SecretStore`` factory under ``name``."""

    _secret_store_registry.register(name, factory)


def get_secret_store(name: str, *args: Any, **kwargs: Any) -> SecretStore:
    """Instantiate the ``SecretStore`` registered as ``name``."""

    return _secret_store_registry.create(name, *args, **kwargs)


def available_secret_stores() -> tuple[str, ...]:
    """Return the identifiers of registered ``SecretStore`` factories."""

    return _secret_store_registry.available()


def register_knowledge_repository(name: str, factory: Callable[..., KnowledgeRepository]) -> None:
    """Register a ``KnowledgeRepository`` factory under ``name``."""

    _knowledge_registry.register(name, factory)


def get_knowledge_repository(
    name: str, *args: Any, **kwargs: Any
) -> KnowledgeRepository:
    """Instantiate the ``KnowledgeRepository`` registered as ``name``."""

    return _knowledge_registry.create(name, *args, **kwargs)


def available_knowledge_repositories() -> tuple[str, ...]:
    """Return the identifiers of registered ``KnowledgeRepository`` factories."""

    return _knowledge_registry.available()


def register_inference_client(name: str, factory: Callable[..., InferenceClient]) -> None:
    """Register an ``InferenceClient`` factory under ``name``."""

    _inference_registry.register(name, factory)


def get_inference_client(name: str, *args: Any, **kwargs: Any) -> InferenceClient:
    """Instantiate the ``InferenceClient`` registered as ``name``."""

    return _inference_registry.create(name, *args, **kwargs)


def available_inference_clients() -> tuple[str, ...]:
    """Return the identifiers of registered ``InferenceClient`` factories."""

    return _inference_registry.available()
