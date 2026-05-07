async function loadItems() {
    const response = await fetch('/api/items');

    if (!response.ok) {
        throw new Error(`Failed to load items: ${response.status}`);
    }

    const data = await response.json();
    return Array.isArray(data.items) ? data.items : [];
}

export default loadItems;
