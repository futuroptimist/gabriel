from __future__ import annotations

from collections.abc import Iterable

import pytest

from gabriel.common import (
    InferenceClient,
    InferenceResult,
    KnowledgeRepository,
    SecretStore,
    ServiceRegistry,
    available_inference_clients,
    available_knowledge_repositories,
    available_secret_stores,
    get_inference_client,
    get_knowledge_repository,
    get_secret_store,
    register_inference_client,
    register_knowledge_repository,
    register_secret_store,
)


class MemorySecretStore(SecretStore):
    """Simple in-memory secret store used to exercise the registry helpers."""

    def __init__(self) -> None:
        self._data: dict[tuple[str, str], str] = {}

    def store(self, service: str, username: str, secret: str) -> None:  # noqa: D401
        self._data[(service, username)] = secret

    def retrieve(self, service: str, username: str) -> str | None:  # noqa: D401
        return self._data.get((service, username))

    def delete(self, service: str, username: str) -> None:  # noqa: D401
        self._data.pop((service, username), None)


class MemoryKnowledgeRepository(KnowledgeRepository):
    """In-memory knowledge repository for exercising the registry plumbing."""

    def __init__(self) -> None:
        self._notes: list[str] = []

    def add(self, note: str) -> None:  # noqa: D401
        self._notes.append(note)

    def search(
        self,
        query: str,
        *,
        required_tags: Iterable[str] | None = None,
        limit: int | None = None,
    ) -> list[str]:  # noqa: D401
        del required_tags
        matches = [note for note in self._notes if query.lower() in note.lower()]
        if limit is None:
            return matches
        return matches[: max(limit, 0)]


class EchoInferenceClient(InferenceClient):
    """Inference client that echoes prompts for registry testing."""

    def infer(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float | None = None,
        metadata: dict[str, str] | None = None,
    ) -> InferenceResult:
        response_metadata = {
            "model": model or "echo",
            "temperature": temperature,
        }
        if metadata:
            response_metadata.update(metadata)
        return InferenceResult(text=prompt, model=response_metadata["model"], metadata=response_metadata)


def test_service_registry_handles_duplicates_and_missing() -> None:
    registry: ServiceRegistry[int] = ServiceRegistry()
    registry.register("one", lambda: 1)

    assert registry.available() == ("one",)  # nosec B101
    assert registry.create("one") == 1  # nosec B101

    with pytest.raises(ValueError):
        registry.register("one", lambda: 2)

    with pytest.raises(LookupError):
        registry.create("missing")


def test_secret_store_registry_round_trip() -> None:
    name = "memory-secret-test"
    register_secret_store(name, MemorySecretStore)
    store = get_secret_store(name)

    store.store("svc", "alice", "token")
    assert store.retrieve("svc", "alice") == "token"  # nosec B101
    store.delete("svc", "alice")
    assert store.retrieve("svc", "alice") is None  # nosec B101
    assert name in available_secret_stores()  # nosec B101


def test_knowledge_repository_registry_round_trip() -> None:
    name = "memory-knowledge-test"
    register_knowledge_repository(name, MemoryKnowledgeRepository)
    repo = get_knowledge_repository(name)

    repo.add("Keep software patched")
    repo.add("Review sshd_config")

    assert repo.search("patched") == ["Keep software patched"]  # nosec B101
    assert name in available_knowledge_repositories()  # nosec B101


def test_inference_client_registry_round_trip() -> None:
    name = "echo-client-test"
    register_inference_client(name, EchoInferenceClient)
    client = get_inference_client(name)

    result = client.infer("hello", model="custom", metadata={"id": "123"})

    assert result.text == "hello"  # nosec B101
    assert result.model == "custom"  # nosec B101
    assert result.metadata["id"] == "123"  # nosec B101
    assert name in available_inference_clients()  # nosec B101
