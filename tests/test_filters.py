from unittest.mock import Mock

import pytest
from aiogram.types import Message

from filters.custom import TextOrCommand


@pytest.mark.asyncio
async def test_text_or_command_exact_match():
    # Arrange
    filter_instance = TextOrCommand("hello_world")
    message = Mock(spec=Message)
    message.text = "hello_world"
    
    # Act
    result = await filter_instance(message)
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_text_or_command_case_insensitive():
    # Arrange
    filter_instance = TextOrCommand("hello_world")
    message = Mock(spec=Message)
    message.text = "hello World" 
    result = await filter_instance(message)
    assert result is True

@pytest.mark.asyncio
async def test_text_or_command_command_style():
    filter_instance = TextOrCommand("start")
    message = Mock(spec=Message)
    message.text = "/start"
    result = await filter_instance(message)
    assert result is True

@pytest.mark.asyncio
async def test_text_or_command_whitespace_handling():
    # "hello world" -> "hello_world"
    filter_instance = TextOrCommand("hello world") 
    
    message = Mock(spec=Message)
    # "hello   world" -> "hello_world" (via split/join)
    message.text = "hello   world"
    
    # Act
    result = await filter_instance(message)
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_text_or_command_mismatch():
    # Arrange
    filter_instance = TextOrCommand("foo")
    message = Mock(spec=Message)
    message.text = "bar"
    
    # Act
    result = await filter_instance(message)
    
    # Assert
    assert result is False

@pytest.mark.asyncio
async def test_text_or_command_no_text():
    # Arrange
    filter_instance = TextOrCommand("foo")
    message = Mock(spec=Message)
    message.text = None
    
    # Act
    result = await filter_instance(message)
    
    # Assert
    assert result is False
