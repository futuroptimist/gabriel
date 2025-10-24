"""Common interfaces and service implementations shared across Gabriel modules."""

from __future__ import annotations

from .interfaces import (
    EnvelopeEncryptor,
    InferenceClient,
    KeyManager,
    KnowledgeRepository,
    SecretStore,
)
from .scratch import ScratchSpace, scratch_space
from .secret_store import (
    DEFAULT_SECRET_STORE,
    SECRET_ENV_PREFIX,
    KeyringSecretStore,
    _env_secret_key,
    read_secret_from_input,
)
from .vector_store import MAX_VECTOR_TTL, SecureVectorStore, VectorRecord

__all__ = [
    "ScratchSpace",
    "scratch_space",
    "SecureVectorStore",
    "EnvelopeEncryptor",
    "InferenceClient",
    "KeyManager",
    "KnowledgeRepository",
    "SecretStore",
    "DEFAULT_SECRET_STORE",
    "KeyringSecretStore",
    "SECRET_ENV_PREFIX",
    "_env_secret_key",
    "read_secret_from_input",
    "MAX_VECTOR_TTL",
    "VectorRecord",
]
