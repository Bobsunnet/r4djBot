import logging
from pathlib import Path

from aiohttp import web

from db_handler.db_class import db_handler

logger = logging.getLogger(__name__)

# Path to webapp files
WEBAPP_DIR = Path(__file__).parent.parent / "webapp"

router = web.RouteTableDef()


@router.get("/")
async def handle_index(request):
    """Serve the main Web App HTML file."""
    index_path = WEBAPP_DIR / "index.html"
    return web.FileResponse(index_path)


@router.get("/static/{filename}")
async def handle_static(request):
    """Serve static files (CSS, JS)."""
    filename = request.match_info["filename"]
    file_path = WEBAPP_DIR / filename

    if not file_path.exists():
        return web.Response(status=404, text="File not found")

    return web.FileResponse(file_path)


@router.get("/api/items")
async def handle_api_items(request):
    """Return all items as JSON."""
    try:
        items = db_handler.get_items_json()
        return web.json_response({"items": items})
    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        return web.json_response({"error": "Failed to fetch items"}, status=500)


async def start_server(host="0.0.0.0", port=8080):
    """Start the aiohttp web server."""
    app = web.Application()

    # Routes
    app.router.add_routes(router)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info(f"Web server started at http://{host}:{port}")

    # Keep server running
    return runner
