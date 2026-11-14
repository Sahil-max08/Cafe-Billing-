/**
 * Campus Cafe POS - Billing & Checkout Engine
 */

class POSBillingApp {
    constructor() {
        this.cart = new Map(); // itemId -> { id, name, price, category, quantity }
        this.subtotal = 0;
        this.gstRate = 5.0;
        this.discount = 0;
        this.grandTotal = 0;
        this.paymentMethod = 'Cash';

        this.init();
    }

    init() {
        this.bindSearchAndCategoryEvents();
        this.bindPaymentMethodEvents();
        this.recalculate();
    }

    bindSearchAndCategoryEvents() {
        const searchInput = document.getElementById('menuSearchInput');
        const clearBtn = document.getElementById('clearSearchBtn');
        const tabs = document.querySelectorAll('.category-tab');

        if (searchInput) {
            searchInput.addEventListener('input', () => {
                if (clearBtn) clearBtn.style.display = searchInput.value ? 'block' : 'none';
                this.filterMenu();
            });
        }

        if (clearBtn && searchInput) {
            clearBtn.addEventListener('click', () => {
                searchInput.value = '';
                clearBtn.style.display = 'none';
                this.filterMenu();
                searchInput.focus();
            });
        }

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.filterMenu();
            });
        });
    }

    bindPaymentMethodEvents() {
        const options = document.querySelectorAll('.payment-option');
        options.forEach(opt => {
            opt.addEventListener('click', () => {
                options.forEach(o => o.classList.remove('active'));
                opt.classList.add('active');
                const radio = opt.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    this.paymentMethod = radio.value;
                }
            });
        });
    }

    filterMenu() {
        const query = (document.getElementById('menuSearchInput')?.value || '').toLowerCase().trim();
        const activeTab = document.querySelector('.category-tab.active');
        const selectedCategory = activeTab ? activeTab.getAttribute('data-category').toLowerCase() : 'all';

        const cards = document.querySelectorAll('.menu-card');
        let visibleCount = 0;

        cards.forEach(card => {
            const name = (card.getAttribute('data-name') || '').toLowerCase();
            const cat = (card.getAttribute('data-category') || '').toLowerCase();

            const matchesCategory = selectedCategory === 'all' || cat === selectedCategory;
            const matchesQuery = !query || name.includes(query) || cat.includes(query);

            if (matchesCategory && matchesQuery) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        const noItemsEl = document.getElementById('noItemsFound');
        if (noItemsEl) {
            noItemsEl.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    addToCart(id, name, price, category) {
        if (this.cart.has(id)) {
            const item = this.cart.get(id);
            item.quantity += 1;
        } else {
            this.cart.set(id, {
                id: id,
                name: name,
                price: parseFloat(price),
                category: category,
                quantity: 1
            });
        }

        showToast(`Added ${name} to order`, 'info');
        this.recalculate();
    }

    updateQuantity(id, delta) {
        if (!this.cart.has(id)) return;

        const item = this.cart.get(id);
        const newQty = item.quantity + delta;

        if (newQty <= 0) {
            this.cart.delete(id);
        } else {
            item.quantity = newQty;
        }

        this.recalculate();
    }

    removeFromCart(id) {
        if (this.cart.has(id)) {
            this.cart.delete(id);
            this.recalculate();
        }
    }

    clearCart() {
        if (this.cart.size === 0) return;
        if (confirm('Are you sure you want to clear the current order?')) {
            this.cart.clear();
            this.recalculate();
            showToast('Order cart cleared.', 'info');
        }
    }

    setDiscount(amount) {
        const input = document.getElementById('discountInput');
        if (input) input.value = amount;
        this.discount = parseFloat(amount) || 0;
        this.recalculate();
    }

    onDiscountChange() {
        const input = document.getElementById('discountInput');
        this.discount = Math.max(0, parseFloat(input?.value) || 0);
        this.recalculate();
    }

    onGstChange(rate) {
        this.gstRate = parseFloat(rate) || 0;
        this.recalculate();
    }

    recalculate() {
        let sub = 0;
        let totalItems = 0;

        for (const [_, item] of this.cart) {
            sub += item.price * item.quantity;
            totalItems += item.quantity;
        }

        this.subtotal = sub;

        // Discount validation
        let appliedDiscount = Math.min(this.discount, this.subtotal);
        if (appliedDiscount < 0) appliedDiscount = 0;

        const taxable = Math.max(0, this.subtotal - appliedDiscount);
        const gstAmount = (taxable * this.gstRate) / 100.0;
        this.grandTotal = taxable + gstAmount;

        this.renderCart(totalItems, gstAmount);
    }

    renderCart(totalItems, gstAmount) {
        const cartEmptyState = document.getElementById('cartEmptyState');
        const cartItemsList = document.getElementById('cartItemsList');
        const countBadge = document.getElementById('cartCountBadge');
        const displaySubtotal = document.getElementById('displaySubtotal');
        const displayGst = document.getElementById('displayGst');
        const displayGrandTotal = document.getElementById('displayGrandTotal');

        if (countBadge) countBadge.textContent = `${totalItems} items`;
        if (displaySubtotal) displaySubtotal.textContent = formatCurrency(this.subtotal);
        if (displayGst) displayGst.textContent = formatCurrency(gstAmount);
        if (displayGrandTotal) displayGrandTotal.textContent = formatCurrency(this.grandTotal);

        if (this.cart.size === 0) {
            if (cartEmptyState) cartEmptyState.style.display = 'flex';
            if (cartItemsList) cartItemsList.style.display = 'none';
            return;
        }

        if (cartEmptyState) cartEmptyState.style.display = 'none';
        if (cartItemsList) {
            cartItemsList.style.display = 'flex';
            let html = '';

            for (const [id, item] of this.cart) {
                const itemTotal = item.price * item.quantity;
                html += `
                    <div class="cart-row">
                        <div class="cart-row-info">
                            <span class="cart-row-title">${item.name}</span>
                            <span class="cart-row-price">${formatCurrency(item.price)} each</span>
                        </div>
                        <div class="cart-row-controls">
                            <button type="button" class="qty-btn" onclick="posApp.updateQuantity(${id}, -1)">&minus;</button>
                            <span class="qty-val">${item.quantity}</span>
                            <button type="button" class="qty-btn" onclick="posApp.updateQuantity(${id}, 1)">&plus;</button>
                        </div>
                        <span class="cart-row-total">${formatCurrency(itemTotal)}</span>
                        <button type="button" class="cart-row-delete" onclick="posApp.removeFromCart(${id})" title="Remove item">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                    </div>
                `;
            }

            cartItemsList.innerHTML = html;
        }
    }

    async submitOrder() {
        if (this.cart.size === 0) {
            showToast('Please add at least one menu item to the order.', 'error');
            return;
        }

        const btn = document.getElementById('btnCompleteOrder');
        const btnText = btn?.querySelector('.btn-text');
        const btnSpinner = btn?.querySelector('.btn-spinner');

        const customerName = document.getElementById('customerName')?.value?.trim() || 'Walk-in Customer';
        const customerPhone = document.getElementById('customerPhone')?.value?.trim() || '';

        const orderItems = [];
        for (const [id, item] of this.cart) {
            orderItems.push({
                id: item.id,
                quantity: item.quantity
            });
        }

        // Set Loading State
        if (btn) btn.disabled = true;
        if (btnText) btnText.style.display = 'none';
        if (btnSpinner) btnSpinner.style.display = 'inline-block';

        try {
            const payload = {
                customer_name: customerName,
                customer_phone: customerPhone,
                items: orderItems,
                gst_rate: this.gstRate,
                discount_amount: this.discount,
                payment_method: this.paymentMethod
            };

            const response = await fetch('/api/bills', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success && data.bill) {
                showToast(`Bill #${data.bill.invoice_number} created successfully!`, 'success');

                // Clear current order
                this.cart.clear();
                const nameInput = document.getElementById('customerName');
                const phoneInput = document.getElementById('customerPhone');
                const discInput = document.getElementById('discountInput');
                if (nameInput) nameInput.value = '';
                if (phoneInput) phoneInput.value = '';
                if (discInput) discInput.value = '0';
                this.discount = 0;
                this.recalculate();

                // Open Receipt Modal automatically for printing
                openReceiptModal(data.bill.id);
            } else {
                showToast(data.error || 'Failed to complete transaction.', 'error');
            }
        } catch (err) {
            console.error('Order error:', err);
            showToast('Network error while processing order.', 'error');
        } finally {
            if (btn) btn.disabled = false;
            if (btnText) btnText.style.display = 'inline-block';
            if (btnSpinner) btnSpinner.style.display = 'none';
        }
    }
}

// Global instance
let posApp;
document.addEventListener('DOMContentLoaded', () => {
    posApp = new POSBillingApp();
});
