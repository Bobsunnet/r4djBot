import loadItems from './api.js';
import escapeHtml from './utils.js';
// Initialize Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// State
let allItems = [];
let cart = []; // Now stores {item, quantity} objects

// Parse URL Parameters

const urlParams = new URLSearchParams(window.location.search);
const workDays = parseInt(urlParams.get('work_days'));

// DOM Elements
const searchInput = document.getElementById('searchInput');
const itemsList = document.getElementById('itemsList');
const cartBtn = document.getElementById('cartBtn');
const cartCount = document.getElementById('cartCount');
const cartOverlay = document.getElementById('cartOverlay');
const closeCart = document.getElementById('closeCart');
const cartItems = document.getElementById('cartItems');
const cartTotal = document.getElementById('cartTotal');
const workDaysDisplay = document.getElementById('workDaysDisplay');
if (workDaysDisplay) {
    workDaysDisplay.textContent = workDays;
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
    const inputField = document.getElementById(`qty-${itemId}`);
    const inputValue = parseInt(inputField.value)
    if (inputValue <= 0) 
        return;

    const inCartQty = getCartQuantity(itemId);
    if (inCartQty + inputValue <= item.amount) {
        setCartQuantity(itemId, inCartQty + inputValue);
    }
    updateAddButton(inputValue, itemId);
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
        itemsList.innerHTML = '<div class="loading">По такому запиту нічого не знайдено =(</div>';
        return;
    }

    itemsList.innerHTML = items.map(item => {
        const quantity = getCartQuantity(item.id);
        return `
        <div class="item-card">
            <div class="item-info">
                <div class="item-name">${escapeHtml(item.name)}</div>
                ${item.desc ? `<div class="item-desc">${escapeHtml(item.desc)}</div>` : ''}
                <div class="item-price">Доступно: ${item.amount}</div>
            </div>
            <div class="quantity-container">
                <div class="quantity-info">
                    <span class="quantity-text">Додано: ${escapeHtml(quantity)}</span>
                </div>
                <div class="quantity-controls">
                    <input type="number" id="qty-${item.id}" value=1 min="1" max="${item.amount}" class="qty-display">
                    <button class="qty-btn" id="qty-btn-${item.id}" onclick="addToCart(${item.id})" ${((quantity + 1) > item.amount) ? 'disabled' : ''}>+</button>
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
    cartTotal.textContent = total*workDays;
    updateSendButton(totalItems);
    renderCart();
}

function updateSendButton() {
    const params = {
        text: "Замовити",
        is_active: false,
        color: "#bfbfbf",
    }
    if (cart.length > 0){
        params.is_active = true;
        params.color = "#40a7e3";
    }

    tg.MainButton.setParams(params);
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

function updateAddButton(value, itemId) {
    const item_amount = allItems.find(i => i.id == itemId).amount;
    value = parseInt(value);
    const addButton = document.getElementById(`qty-btn-${itemId}`);
    const inCartAmount = getCartQuantity(itemId);

    if ((value < 1) || (value > item_amount) || (value + inCartAmount > item_amount)) {
        addButton.disabled = true;
    } else {
        addButton.disabled = false;
    }
}

itemsList.addEventListener('input', (e) => {
    updateAddButton(parseInt(e.target.value), parseInt(e.target.id.split('-')[1]));
})


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
tg.MainButton.show();

window.addToCart = addToCart;
window.increaseInCartAmount = increaseInCartAmount;
window.decreaseInCartAmount = decreaseInCartAmount;
