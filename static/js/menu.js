/**
 * Menu Management Client Module
 */

class MenuManager {
    constructor() {
        this.activeDeleteId = null;
        this.init();
    }

    init() {
        // Modal backdrop click
        const formModal = document.getElementById('itemFormModal');
        const deleteModal = document.getElementById('deleteConfirmModal');

        if (formModal) {
            formModal.addEventListener('click', (e) => {
                if (e.target === formModal) this.closeFormModal();
            });
        }

        if (deleteModal) {
            deleteModal.addEventListener('click', (e) => {
                if (e.target === deleteModal) this.closeDeleteModal();
            });
        }
    }

    openAddModal() {
        const modal = document.getElementById('itemFormModal');
        const title = document.getElementById('modalTitle');
        const form = document.getElementById('menuItemForm');

        if (title) title.innerHTML = '<i class="fa-solid fa-plus-circle"></i> Add Food Item';
        if (form) form.reset();

        document.getElementById('itemId').value = '';
        document.getElementById('itemAvailable').checked = true;

        if (modal) modal.classList.add('active');
        document.getElementById('itemName')?.focus();
    }

    openEditModal(id, name, category, price, isAvailable, description) {
        const modal = document.getElementById('itemFormModal');
        const title = document.getElementById('modalTitle');

        if (title) title.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Menu Item';

        document.getElementById('itemId').value = id;
        document.getElementById('itemName').value = name;
        document.getElementById('itemCategory').value = category;
        document.getElementById('itemPrice').value = price;
        document.getElementById('itemAvailable').checked = parseInt(isAvailable) === 1;
        document.getElementById('itemDescription').value = description || '';

        if (modal) modal.classList.add('active');
        document.getElementById('itemName')?.focus();
    }

    closeFormModal() {
        const modal = document.getElementById('itemFormModal');
        if (modal) modal.classList.remove('active');
    }

    async saveItem(event) {
        event.preventDefault();

        const id = document.getElementById('itemId').value;
        const name = document.getElementById('itemName').value.trim();
        const category = document.getElementById('itemCategory').value;
        const price = parseFloat(document.getElementById('itemPrice').value);
        const isAvailable = document.getElementById('itemAvailable').checked;
        const description = document.getElementById('itemDescription').value.trim();

        if (!name || !category || isNaN(price)) {
            showToast('Please fill all required fields.', 'error');
            return;
        }

        if (price < 0) {
            showToast('Price cannot be negative.', 'error');
            return;
        }

        const payload = {
            name: name,
            category: category,
            price: price,
            is_available: isAvailable,
            description: description
        };

        const btn = document.getElementById('btnSaveItem');
        if (btn) btn.disabled = true;

        try {
            const url = id ? `/api/menu/${id}` : '/api/menu';
            const method = id ? 'PUT' : 'POST';

            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (data.success) {
                showToast(data.message || 'Item saved successfully!', 'success');
                this.closeFormModal();
                // Reload page to refresh filter and table states
                setTimeout(() => window.location.reload(), 400);
            } else {
                showToast(data.error || 'Failed to save menu item.', 'error');
            }
        } catch (err) {
            console.error('Error saving item:', err);
            showToast('Network error while saving item.', 'error');
        } finally {
            if (btn) btn.disabled = false;
        }
    }

    confirmDelete(id, name) {
        this.activeDeleteId = id;
        const nameEl = document.getElementById('deleteItemName');
        const modal = document.getElementById('deleteConfirmModal');

        if (nameEl) nameEl.textContent = `"${name}"`;
        if (modal) modal.classList.add('active');
    }

    closeDeleteModal() {
        this.activeDeleteId = null;
        const modal = document.getElementById('deleteConfirmModal');
        if (modal) modal.classList.remove('active');
    }

    async executeDelete() {
        if (!this.activeDeleteId) return;

        const btn = document.getElementById('confirmDeleteBtn');
        if (btn) btn.disabled = true;

        try {
            const res = await fetch(`/api/menu/${this.activeDeleteId}`, {
                method: 'DELETE'
            });
            const data = await res.json();

            if (data.success) {
                showToast('Menu item deleted.', 'info');
                const row = document.getElementById(`menuRow-${this.activeDeleteId}`);
                if (row) row.remove();
                this.closeDeleteModal();
            } else {
                showToast(data.error || 'Failed to delete item.', 'error');
            }
        } catch (err) {
            showToast('Network error while deleting item.', 'error');
        } finally {
            if (btn) btn.disabled = false;
        }
    }

    async toggleStock(id) {
        try {
            const res = await fetch(`/api/menu/${id}/toggle`, {
                method: 'PATCH'
            });
            const data = await res.json();

            if (data.success) {
                const badge = document.getElementById(`stockBadge-${id}`);
                if (badge) {
                    if (data.is_available === 1) {
                        badge.className = 'stock-status-badge stock-in';
                        badge.innerHTML = '<i class="fa-solid fa-circle-check"></i> In Stock';
                    } else {
                        badge.className = 'stock-status-badge stock-out';
                        badge.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Out of Stock';
                    }
                }
                showToast(data.message, 'success');
            } else {
                showToast(data.error || 'Failed to update stock status.', 'error');
            }
        } catch (err) {
            showToast('Network error while toggling stock.', 'error');
        }
    }
}

let menuApp;
document.addEventListener('DOMContentLoaded', () => {
    menuApp = new MenuManager();
});
