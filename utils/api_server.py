import logging
from pathlib import Path

from aiohttp import web

from db_handler.crud import get_items
from db_handler.db_helper import db_helper

logger = logging.getLogger(__name__)

# Path to webapp files
WEBAPP_DIR = Path(__file__).parent.parent / "webapp"

router = web.RouteTableDef()


async def get_items_json():
    """Return all items formatted for the WebApp JSON API."""
    from config import settings

    async with db_helper.session_getter() as session:
        items = await get_items(session=session)

        return [
            {
                "id": item.row_order,
                "name": item.name,
                "desc": item.description,
                "amount": item.amount,
                "price": item.price * settings.price_multiplier,
            }
            for item in items
        ]


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

    return web.FileResponse(file_path, headers={"Cache-Control": "max-age=86400"})


@router.get("/api/items")
async def handle_api_items(request):
    """Return all items as JSON."""
    try:
        items = await get_items_json()
        return web.json_response({"items": items})
    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        return web.json_response({"error": "Failed to fetch items"}, status=500)


async def start_server(host="127.0.0.1", port=8000):
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
