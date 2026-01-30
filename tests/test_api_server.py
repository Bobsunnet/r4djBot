from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web

from utils.api_server import (
    get_items_json,
    handle_api_items,
    handle_index,
    handle_static,
    router,
)


@pytest.fixture
def test_app():
    """Create a test aiohttp application."""
    app = web.Application()
    app.router.add_routes(router)
    return app


@pytest.mark.asyncio
async def test_get_items_json():
    """Test the get_items_json function returns correctly formatted data."""
    # Arrange: Mock the database session and items
    mock_item = MagicMock()
    mock_item.row_order = 1
    mock_item.name = "Мікшерний пульт"
    mock_item.description = "Професійний пульт Yamaha"
    mock_item.amount = 5
    mock_item.price = 1000.0
    mock_item.hash_code = "abc123"
    
    with patch("utils.api_server.db_helper.session_getter") as mock_session_getter:
        with patch("utils.api_server.get_items", new_callable=AsyncMock) as mock_get_items:
            # Setup mock context manager for session
            mock_session = AsyncMock()
            mock_session_getter.return_value.__aenter__.return_value = mock_session
            mock_session_getter.return_value.__aexit__.return_value = None
            
            # Mock get_items to return our test item
            mock_get_items.return_value = [mock_item]
            
            # Act
            result = await get_items_json()
            
            # Assert
            assert len(result) == 1
            assert result[0]["id"] == 1
            assert result[0]["name"] == "Мікшерний пульт"
            assert result[0]["desc"] == "Професійний пульт Yamaha"
            assert result[0]["amount"] == 5
            # Price should be multiplied by settings.price_multiplier (0.5)
            assert result[0]["price"] == 500.0
            assert result[0]["hash_code"] == "abc123"


@pytest.mark.asyncio
async def test_handle_index(aiohttp_client, test_app):
    """Test that the index route serves the HTML file."""
    client = await aiohttp_client(test_app)
    
    # Act
    resp = await client.get("/")
    
    # Assert
    assert resp.status == 200
    assert resp.content_type == "text/html"


@pytest.mark.asyncio
async def test_handle_static_existing_file(aiohttp_client, test_app):
    """Test serving an existing static file."""
    client = await aiohttp_client(test_app)
    
    # Act: Request a known static file (adjust filename if needed)
    resp = await client.get("/static/app.js")
    
    # Assert
    assert resp.status == 200
    # Check cache header is set
    assert "Cache-Control" in resp.headers


@pytest.mark.asyncio
async def test_handle_static_nonexistent_file(aiohttp_client, test_app):
    """Test that requesting a non-existent file returns 404."""
    client = await aiohttp_client(test_app)
    
    # Act
    resp = await client.get("/static/nonexistent.js")
    
    # Assert
    assert resp.status == 404
    text = await resp.text()
    assert "File not found" in text


@pytest.mark.asyncio
async def test_handle_api_items_success(aiohttp_client, test_app):
    """Test the /api/items endpoint with successful data retrieval."""
    client = await aiohttp_client(test_app)
    
    # Arrange: Mock get_items_json
    mock_items = [
        {
            "id": 1,
            "name": "LED екран",
            "desc": "3x2 метри",
            "amount": 2,
            "price": 2500.0,
            "hash_code": "led123"
        }
    ]
    
    with patch("utils.api_server.get_items_json", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_items
        
        # Act
        resp = await client.get("/api/items")
        
        # Assert
        assert resp.status == 200
        json_data = await resp.json()
        assert "items" in json_data
        assert len(json_data["items"]) == 1
        assert json_data["items"][0]["name"] == "LED екран"


@pytest.mark.asyncio
async def test_handle_api_items_error(aiohttp_client, test_app):
    """Test the /api/items endpoint handles errors gracefully."""
    client = await aiohttp_client(test_app)
    
    # Arrange: Mock get_items_json to raise an exception
    with patch("utils.api_server.get_items_json", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Database connection failed")
        
        # Act
        resp = await client.get("/api/items")
        
        # Assert
        assert resp.status == 500
        json_data = await resp.json()
        assert "error" in json_data
        assert json_data["error"] == "Failed to fetch items"
