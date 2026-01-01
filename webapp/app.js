// Initialize Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// State
let allItems = [];
let cart = []; // Now stores {item, quantity} objects

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
        renderItemsList(allItems);
    } catch (error) {
        itemsList.innerHTML = '<div class="loading">Failed to load items</div>';
        console.error('Error loading items:', error);
    }
}

// Get quantity of item in cart
function getCartQuantity(itemId) {
    const cartItem = cart.find(c => c.item.id === itemId);
    return cartItem ? cartItem.quantity : 0;
}

// Update quantity in cart
function setCartQuantity(itemId, quantity) {
    const item = allItems.find(i => i.id === itemId);
    if (!item) return;

    const cartIndex = cart.findIndex(c => c.item.id === itemId);
    
    if (quantity <= 0) {
        // Remove from cart
        if (cartIndex > -1) {
            cart.splice(cartIndex, 1);
        }
    } else {
        // Add or update
        if (cartIndex > -1) {
            cart[cartIndex].quantity = quantity;
        } else {
            cart.push({ item, quantity });
        }
    }
    
    updateCartUI();
    renderItemsList(searchInput.value ? 
        allItems.filter(i => i.name.toLowerCase().includes(searchInput.value.toLowerCase())) : 
        allItems
    );
}

// // Increase quantity
// function increaseAmount(itemId) {
//     const currentQty = getCartQuantity(itemId);
//     const item = allItems.find(i => i.id === itemId);
    
//     // Check if we can add more (don't exceed available amount)
//     if (item && currentQty < item.amount) {
//         setCartQuantity(itemId, currentQty + 1);
//     }
// }

// // Decrease quantity
// function decreaseAmount(itemId) {
//     const currentQty = getCartQuantity(itemId);
//     if (currentQty > 0) {
//         setCartQuantity(itemId, currentQty - 1);
//     }
// }

// Render items list
function renderItemsList(items) {
    if (items.length === 0) {
        itemsList.innerHTML = '<div class="loading">No items found</div>';
        return;
    }

    itemsList.innerHTML = items.map(item => {
        const qty = getCartQuantity(item.id);
        return `
        <div class="item-card">
            <div class="item-info">
                <div class="item-name">${escapeHtml(item.name)}</div>
                ${item.desc ? `<div class="item-desc">${escapeHtml(item.desc)}</div>` : ''}
                <div class="item-price">Available: ${item.amount}</div>
            </div>
            <div class="quantity-controls">
                // <button class="qty-btn" onclick="decreaseAmount(${item.id})" ${qty === 0 ? 'disabled' : ''}>−</button>
                <input type="number" value="${qty}" min="0" max="${item.amount}" class="qty-display">
                // <button class="qty-btn" onclick="increaseAmount(${item.id})" ${qty >= item.amount ? 'disabled' : ''}>+</button>
            </div>
        </div>
    `;
    }).join('');
}

// Search functionality
searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = allItems.filter(item => 
        item.name.toLowerCase().includes(query) ||
        (item.desc && item.desc.toLowerCase().includes(query))
    );
    renderItemsList(filtered);
});

// Cart functions
function updateCartUI() {
    const totalItems = cart.reduce((sum, c) => sum + c.quantity, 0);
    cartCount.textContent = totalItems;
    
    const total = cart.reduce((sum, c) => sum + (c.item.price * c.quantity), 0);
    cartTotal.textContent = total;

    // Update Telegram MainButton
    if (cart.length > 0) {
        tg.MainButton.setText(`Send Order (${totalItems} items)`);
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

    cartItems.innerHTML = cart.map(cartItem => `
        <div class="cart-item">
            <div class="cart-item-info">
                <div class="cart-item-name">${escapeHtml(cartItem.item.name)}</div>
                <div class="cart-item-price">${cartItem.item.price} × ${cartItem.quantity} = ${cartItem.item.price * cartItem.quantity}</div>
            </div>
            <div class="quantity-controls">
                <button class="qty-btn-small" onclick="decreaseAmount(${cartItem.item.id})">−</button>
                <span class="qty-display-small">${cartItem.quantity}</span>
                <button class="qty-btn-small" onclick="increaseAmount(${cartItem.item.id})">+</button>
            </div>
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
        items: cart.map(cartItem => ({
            id: cartItem.item.id,
            name: cartItem.item.name,
            price: cartItem.item.price,
            quantity: cartItem.quantity
        })),
        total: cart.reduce((sum, c) => sum + (c.item.price * c.quantity), 0)
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
