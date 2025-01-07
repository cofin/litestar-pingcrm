from __future__ import annotations

from typing import Any

import click
from litestar.plugins import CLIPluginProtocol, InitPluginProtocol


class CommandLinePlugin(InitPluginProtocol, CLIPluginProtocol):
    """Adds custom commands to the CLI."""

    def on_cli_init(self, cli: click.Group) -> None:  # noqa: PLR0915
        from advanced_alchemy.extensions.litestar.cli import database_group

        @click.group(name="users", invoke_without_command=False, help="Manage application users.")
        @click.pass_context  # pyright: ignore[reportArgumentType]
        def user_management_app(_: dict[str, Any]) -> None:
            """Manage application users."""

        @user_management_app.command(name="create-user", help="Create a user")
        @click.option(
            "--email",
            help="Email of the new user",
            type=click.STRING,
            required=False,
            show_default=False,
        )
        @click.option(
            "--name",
            help="Full name of the new user",
            type=click.STRING,
            required=False,
            show_default=False,
        )
        @click.option(
            "--password",
            help="Password",
            type=click.STRING,
            required=False,
            show_default=False,
        )
        @click.option(
            "--superuser",
            help="Is a superuser",
            type=click.BOOL,
            default=False,
            required=False,
            show_default=False,
            is_flag=True,
        )
        @click.option(
            "--initial-account",
            help="Initial Account to assign",
            type=click.STRING,
            required=False,
            show_default=False,
        )
        def create_user(email: str | None, name: str | None, password: str | None, superuser: bool | None) -> None:
            """Create a user."""
            import anyio
            import click
            from rich import get_console

            from app import config, deps, schemas

            console = get_console()

            async def _create_user(email: str, password: str, name: str | None, superuser: bool = False, initial_account: str | None = None) -> None:
                obj_in = schemas.UserCreate(email=email, name=name, password=password, is_superuser=superuser)
                async with config.alchemy.get_session() as db_session:
                    users_service = await anext(deps.provide_users_service(db_session))
                    user = await users_service.create(data=obj_in.to_dict(), auto_commit=True)
                    console.print(f"User created: {user.email}")

            console.rule("Create a new application user.")
            email = email or click.prompt("Email")
            name = name or click.prompt("Full Name", show_default=False)
            password = password or click.prompt("Password", hide_input=True, confirmation_prompt=True)
            superuser = superuser or click.prompt("Create as superuser?", show_default=True, type=click.BOOL)
            initial_account = superuser or click.prompt("Create as superuser?", show_default=True, type=click.BOOL)

            anyio.run(_create_user, email, name, password, superuser, initial_account)

        @user_management_app.command(name="promote-to-superuser", help="Promotes a user to application superuser")
        @click.option("--email", help="Email of the user", type=click.STRING, required=False, show_default=False)
        def promote_to_superuser(email: str) -> None:
            """Promote to Superuser.

            Args:
                email (str): The email address of the user to promote.
            """
            import anyio
            from rich import get_console

            from app import config, deps, schemas

            console = get_console()

            async def _promote_to_superuser(email: str) -> None:
                async with config.alchemy.get_session() as db_session:
                    users_service = await anext(deps.provide_users_service(db_session))
                    user = await users_service.get_one_or_none(email=email)
                    if user:
                        console.print(f"Promoting user: %{user.email}")
                        user_in = schemas.UserUpdate(
                            email=user.email,
                            is_superuser=True,
                        )
                        user = await users_service.update(
                            item_id=user.id,
                            data=user_in.to_dict(),
                            auto_commit=True,
                        )
                        console.print(f"Upgraded {email} to superuser")
                    else:
                        console.print(f"User not found: {email}")

            console.rule("Promote user to superuser.")
            anyio.run(_promote_to_superuser, email)

        @database_group.command("load-fixtures")
        def load_database_fixtures() -> None:
            import anyio
            from rich import get_console

            console = get_console()

            async def _load_database_fixtures() -> None:
                """Import/Synchronize Database Fixtures."""
                from pathlib import Path

                from advanced_alchemy.utils.fixtures import open_fixture_async
                from rich import get_console

                from app import config, services
                from config import get_settings

                console, settings = get_console(), get_settings()
                fixture_path = Path(settings.db.FIXTURE_PATH)
                async with services.UserService.new(config=config.alchemy) as service:
                    for fixture in await open_fixture_async(fixture_path, "users"):
                        _obj, _created = await service.get_or_upsert(match_fields=["email"], upsert=False, **fixture)
                    await service.repository.session.commit()
                    console.print("User fixtures loaded.")

            console.rule("Loading database fixtures.")
            anyio.run(_load_database_fixtures)

        cli.add_command(user_management_app)
