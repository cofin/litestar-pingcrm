from __future__ import annotations


def run_cli() -> None:
    """Application Entrypoint."""
    import os
    import sys
    from pathlib import Path

    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path))

    from config import get_settings

    settings = get_settings()

    os.environ.setdefault("LITESTAR_APP", settings.app.APP_LOC)
    os.environ.setdefault("LITESTAR_APP_NAME", settings.app.NAME)
    try:
        from litestar.__main__ import run_cli as run_litestar_cli

    except ImportError as exc:
        print(  # noqa: T201
            "Could not load required libraries.  ",
            "Please check your installation and make sure you activated any necessary virtual environment",
        )
        print(exc)  # noqa: T201
        sys.exit(1)
    run_litestar_cli()


if __name__ == "__main__":
    run_cli()
