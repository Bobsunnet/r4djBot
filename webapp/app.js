import loadItems from './api.js';
import escapeHtml from './utils.js';
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
        if (cartIndex > -1) {
            cart.splice(cartIndex, 1);
        }
    } else {
        if (cartIndex > -1) {
            cart[cartIndex].quantity = quantity;
        } else {
            cart.push({ item, quantity });
        }
    }
    
    updateCartUI();    
    renderItemsList(updateFilteredList());
}

function updateFilteredList() {
    const filterString = searchInput.value;
    const filtered = filterString ? 
        allItems.filter(i => 
            i.name.toLowerCase().includes(filterString.toLowerCase()) || 
            i.desc.toLowerCase().includes(filterString.toLowerCase())) : 
        allItems;
    
    return filtered;
}

// Increase quantity
function addToCart(itemId) {
    const item = allItems.find(i => i.id === itemId);
    if (!item) 
        return;

    const inputField = document.getElementById(`qty-${itemId}`);
    const addAmount = inputField ? (parseInt(inputField.value) || 0) : 1;
    if (addAmount <= 0) 
        return;

    const currentQty = getCartQuantity(itemId);
    
    if (currentQty + addAmount <= item.amount) {
        setCartQuantity(itemId, currentQty + addAmount);
        if (inputField) 
            inputField.value = 0;
    }
}

function increaseInCartAmount(itemId) {
    const cartItem = cart.find(c => c.item.id === itemId);
    const itemQuantityElement = document.getElementById(`cart-qty-${itemId}`);
    if (cartItem.quantity + 1 > cartItem.item.amount) return;
    
    itemQuantityElement.textContent = cartItem.quantity + 1;
    cartItem.quantity += 1;
    updateCartUI();
    renderItemsList(updateFilteredList());
}

function decreaseInCartAmount(itemId) {
    const cartItem = cart.find(c => c.item.id === itemId);
    const itemQuantityElement = document.getElementById(`cart-qty-${itemId}`);
    if (cartItem.quantity - 1 < 1) {
        cart.splice(cart.indexOf(cartItem), 1)
        console.log(cart);
        updateCartUI();
        renderItemsList(updateFilteredList());
        return;
    };

    itemQuantityElement.textContent = cartItem.quantity - 1;
    cartItem.quantity -= 1;
    updateCartUI();
    renderItemsList(updateFilteredList());
}

// Render items list
function renderItemsList(items) {
    if (items.length === 0) {
        itemsList.innerHTML = '<div class="loading">No items found</div>';
        return;
    }

    itemsList.innerHTML = items.map(item => {
        const quantity = getCartQuantity(item.id);
        return `
        <div class="item-card">
            <div class="item-info">
                <div class="item-name">${escapeHtml(item.name)}</div>
                ${item.desc ? `<div class="item-desc">${escapeHtml(item.desc)}</div>` : ''}
                <div class="item-price">Available: ${item.amount}</div>
            </div>
            <div class="quantity-container">
                <div class="quantity-info">
                    <span class="quantity-text">Додано: ${escapeHtml(quantity)}</span>
                </div>
                <div class="quantity-controls">
                    <input type="number" id="qty-${item.id}" value=1 min="1" max="${item.amount}" class="qty-display">
                    <button class="qty-btn" onclick="addToCart(${item.id})">+</button>
                </div>
            </div>
        </div>
    `;
    }).join('');
}

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

    renderCart();
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
                <button class="qty-btn-small" onclick="decreaseInCartAmount(${cartItem.item.id})">−</button>
                <span class="qty-display-small" id="cart-qty-${cartItem.item.id}">${cartItem.quantity}</span>
                <button class="qty-btn-small" onclick="increaseInCartAmount(${cartItem.item.id})">+</button>
            </div>
        </div>
    `).join('');
}

searchInput.addEventListener('input', () => {
    renderItemsList(updateFilteredList());
});


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
            name: cartItem.item.name,
            quantity: cartItem.quantity
        }))
    };
    
    tg.sendData(JSON.stringify(orderData));
});

// Initialize
loadItems().then(items => {
    if (items) {
        allItems = items;
        renderItemsList(allItems);
    }
});
updateCartUI();

window.addToCart = addToCart;
window.increaseInCartAmount = increaseInCartAmount;
window.decreaseInCartAmount = decreaseInCartAmount;
