from litestar import Controller, Request, get
from litestar.response import File
from litestar_vite.inertia import InertiaRedirect

from app import config


class SiteController(Controller):
    include_in_schema = False

    @get(path="/", name="home", exclude_from_auth=True)
    async def home(self, request: Request) -> InertiaRedirect:
        """Serve site root."""
        if request.session.get("user_id", False):
            return InertiaRedirect(request, request.url_for("dashboard"))
        return InertiaRedirect(request, request.url_for("login"))

    @get(component="Dashboard/Index", path="/dashboard/", name="dashboard")
    async def dashboard(self) -> dict:
        """Serve Dashboard Page."""
        return {}

    @get(component="Reports/Index", path="/reports/", name="reports")
    async def reports(self) -> dict:
        """Serve Reports Page."""
        return {}

    @get(path="/favicon.svg", name="favicon", exclude_from_auth=True, include_in_schema=False, sync_to_thread=False)
    def favicon(self) -> File:
        """Serve site root."""
        return File(path=f"{config.vite.public_dir}/favicon.svg")
