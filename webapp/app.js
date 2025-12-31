// Initialize Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// State
let allItems = [];
let cart = [];

// DOM Elements
const searchInput = document.getElementById('searchInput');
const itemsList = document.getElementById('itemsList');
const cartBtn = document.getElementById('cartBtn');
const cartCount = document.getElementById('cartCount');
const cartOverlay = document.getElementById('cartOverlay');
const closeCart = document.getElementById('closeCart');
const cartItems = document.getElementById('cartItems');
const cartTotal = document.getElementById('cartTotal');

// Load items from API
async function loadItems() {
    try {
        const response = await fetch('/api/items');
        const data = await response.json();
        allItems = data.items || [];
        renderItems(allItems);
    } catch (error) {
        itemsList.innerHTML = '<div class="loading">Failed to load items</div>';
        console.error('Error loading items:', error);
    }
}

// Render items list
function renderItems(items) {
    if (items.length === 0) {
        itemsList.innerHTML = '<div class="loading">No items found</div>';
        return;
    }

    itemsList.innerHTML = items.map(item => `
        <div class="item-card">
            <div class="item-info">
                <div class="item-name">${escapeHtml(item.name)}</div>
                ${item.desc ? `<div class="item-desc">${escapeHtml(item.desc)}</div>` : ''}
                <div class="item-price">${item.price} </div>
            </div>
            <button 
                class="add-btn ${isInCart(item.id) ? 'in-cart' : ''}" 
                onclick="toggleCart(${item.id})"
            >
                ${isInCart(item.id) ? '✓' : '+'}
            </button>
        </div>
    `).join('');
}

// Search functionality
searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = allItems.filter(item => 
        item.name.toLowerCase().includes(query) ||
        (item.desc && item.desc.toLowerCase().includes(query))
    );
    renderItems(filtered);
});

// Cart functions
function isInCart(itemId) {
    return cart.some(item => item.id === itemId);
}

function toggleCart(itemId) {
    const item = allItems.find(i => i.id === itemId);
    if (!item) return;

    const index = cart.findIndex(i => i.id === itemId);
    if (index > -1) {
        cart.splice(index, 1);
    } else {
        cart.push(item);
    }

    updateCartUI();
    renderItems(searchInput.value ? 
        allItems.filter(i => i.name.toLowerCase().includes(searchInput.value.toLowerCase())) : 
        allItems
    );
}

function updateCartUI() {
    cartCount.textContent = cart.length;
    
    const total = cart.reduce((sum, item) => sum + item.price, 0);
    cartTotal.textContent = total;

    // Update Telegram MainButton
    if (cart.length > 0) {
        tg.MainButton.setText(`Send Order (${cart.length} items)`);
        tg.MainButton.show();
    } else {
        tg.MainButton.hide();
    }
}

function renderCart() {
    if (cart.length === 0) {
        cartItems.innerHTML = '<div class="empty-cart">Your cart is empty</div>';
        return;
    }

    cartItems.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-info">
                <div class="cart-item-name">${escapeHtml(item.name)}</div>
                <div class="cart-item-price">${item.price} </div>
            </div>
            <button class="remove-btn" onclick="toggleCart(${item.id})">−</button>
        </div>
    `).join('');
}

// Show cart overlay
cartBtn.addEventListener('click', () => {
    renderCart();
    cartOverlay.classList.remove('hidden');
});

closeCart.addEventListener('click', () => {
    cartOverlay.classList.add('hidden');
});

// Close cart when clicking outside
cartOverlay.addEventListener('click', (e) => {
    if (e.target === cartOverlay) {
        cartOverlay.classList.add('hidden');
    }
});

// Send data to bot
tg.MainButton.onClick(() => {
    const orderData = {
        items: cart.map(item => ({
            id: item.id,
            name: item.name,
            price: item.price
        })),
        total: cart.reduce((sum, item) => sum + item.price, 0)
    };
    
    tg.sendData(JSON.stringify(orderData));
});

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
loadItems();
updateCartUI();
