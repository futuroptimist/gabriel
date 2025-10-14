"""UI layer aggregating CLI entry points and the bundled viewer."""

from .cli import (
    SECRET_CMD_DELETE,
    SECRET_CMD_GET,
    SECRET_CMD_STORE,
    _env_secret_key,
    _read_secret_from_input,
    main,
)
from .viewer import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    ViewerServer,
    get_viewer_directory,
    serve_viewer,
    start_viewer_server,
)

__all__ = [
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "ViewerServer",
    "get_viewer_directory",
    "serve_viewer",
    "start_viewer_server",
    "SECRET_CMD_STORE",
    "SECRET_CMD_GET",
    "SECRET_CMD_DELETE",
    "_env_secret_key",
    "_read_secret_from_input",
    "main",
]
