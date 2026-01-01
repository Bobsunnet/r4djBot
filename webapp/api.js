async function loadItems() {
    try {
        const response = await fetch('/api/items');
        const data = await response.json();
        return data.items || [];
    } catch (error) {
        console.error('Error loading items:', error);  
    }
}

export default loadItems;