import logging

import requests

URL_SHEET = "https://script.google.com/macros/s/AKfycbyIqo_k_VKMYcqZSiVhiQvsbYlwE0G6OjbvBDeYWZ7Fk09J4lMRXKy1bwK8gRA2Y6SkgA/exec"
logger = logging.getLogger(__name__)


def download_sheets_data(url: str) -> list:
    """Download data from Google Sheets."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            logging.error(
                f"Failed to download data, status code: {response.status_code}"
            )
            return []

    except requests.RequestException as e:
        logging.error(f"Error downloading data: {e}")
        return []


def get_prices_data() -> list:
    """Filters out prices data from Google Sheets."""
    return list(
        filter(lambda row: row[3] or row[4], download_sheets_data(URL_SHEET)[1:])
    )
