/**
 * Campus Cafe POS & Billing System - Main App JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initSidebarToggle();
    cleanOldServiceWorkers();
});

// Clear leftover Service Workers or PWA caches from earlier projects on port 8000
function cleanOldServiceWorkers() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(registrations => {
            for (let reg of registrations) {
                reg.unregister();
            }
        });
    }
    if ('caches' in window) {
        caches.keys().then(keys => {
            for (let k of keys) {
                caches.delete(k);
            }
        });
    }
}

// Live Header Clock
function initClock() {
    const clockText = document.getElementById('clockText');
    if (!clockText) return;

    function update() {
        const now = new Date();
        clockText.textContent = now.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
    }

    update();
    setInterval(update, 1000);
}

// Mobile Sidebar Toggle
function initSidebarToggle() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    const closeBtn = document.getElementById('sidebarCloseBtn');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.add('open');
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
    }
}

// Global Toast System
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'fa-circle-info';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'error') icon = 'fa-triangle-exclamation';

    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Currency Formatter
function formatCurrency(amount) {
    const num = parseFloat(amount) || 0;
    return '₹' + num.toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Global Receipt Modal Controller
async function openReceiptModal(billId) {
    const modal = document.getElementById('receiptModal');
    const body = document.getElementById('receiptModalBody');
    if (!modal || !body) return;

    body.innerHTML = `
        <div style="padding: 40px; text-align: center; color: #64748b;">
            <i class="fa-solid fa-circle-notch fa-spin fa-2x"></i>
            <p style="margin-top: 10px; font-weight: 500;">Loading bill details...</p>
        </div>
    `;
    modal.classList.add('active');

    try {
        const res = await fetch(`/api/bills/${billId}`);
        const data = await res.json();

        if (data.success && data.bill) {
            renderReceiptInModal(data.bill);
        } else {
            body.innerHTML = `<div class="alert alert-error">Failed to load bill: ${data.error || 'Unknown error'}</div>`;
        }
    } catch (err) {
        body.innerHTML = `<div class="alert alert-error">Network error loading receipt.</div>`;
    }
}

function closeReceiptModal() {
    const modal = document.getElementById('receiptModal');
    if (modal) modal.classList.remove('active');
}

function renderReceiptInModal(bill) {
    const body = document.getElementById('receiptModalBody');
    if (!body) return;

    let itemsHtml = '';
    (bill.items || []).forEach(item => {
        itemsHtml += `
            <tr>
                <td class="td-item">
                    <span class="item-line-name">${item.item_name}</span>
                    <small class="item-line-cat">[${item.category}]</small>
                </td>
                <td class="td-qty">${item.quantity}</td>
                <td class="td-rate">${formatCurrency(item.unit_price)}</td>
                <td class="td-amt">${formatCurrency(item.total_price)}</td>
            </tr>
        `;
    });

    const discountRow = bill.discount_amount > 0 ? `
        <div class="total-row discount-row">
            <span>Discount:</span>
            <span>-${formatCurrency(bill.discount_amount)}</span>
        </div>
    ` : '';

    const cgst = (bill.gst_amount / 2).toFixed(2);
    const sgst = (bill.gst_amount / 2).toFixed(2);

    body.innerHTML = `
        <div class="thermal-receipt" id="modalThermalReceipt">
            <div class="receipt-sawtooth-top"></div>

            <div class="receipt-header">
                <div class="cafe-brand">
                    <i class="fa-solid fa-mug-hot"></i>
                    <h2>CAFETERIA BILLING SYSTEM</h2>
                </div>
                <p class="cafe-tagline">College Food Court & Student Center</p>
                <p class="cafe-address">Campus Main Quad &bull; Counter No. 01</p>
                <p class="cafe-gstin">GSTIN: 27AABCC1234F1Z5</p>
            </div>

            <div class="receipt-divider-dashed"></div>

            <div class="receipt-meta-grid">
                <div class="meta-row">
                    <span class="meta-label">INVOICE:</span>
                    <strong class="meta-val">${bill.invoice_number}</strong>
                </div>
                <div class="meta-row">
                    <span class="meta-label">DATE & TIME:</span>
                    <span class="meta-val">${bill.created_at || 'Just Now'}</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">CUSTOMER:</span>
                    <span class="meta-val">${bill.customer_name || 'Walk-in Customer'}</span>
                </div>
                ${bill.customer_phone ? `
                <div class="meta-row">
                    <span class="meta-label">PHONE:</span>
                    <span class="meta-val">${bill.customer_phone}</span>
                </div>` : ''}
                <div class="meta-row">
                    <span class="meta-label">PAYMENT:</span>
                    <strong class="meta-val">${(bill.payment_method || 'CASH').toUpperCase()}</strong>
                </div>
            </div>

            <div class="receipt-divider-dashed"></div>

            <table class="receipt-items-table">
                <thead>
                    <tr>
                        <th class="th-item">ITEM</th>
                        <th class="th-qty">QTY</th>
                        <th class="th-rate">RATE</th>
                        <th class="th-amt">AMOUNT</th>
                    </tr>
                </thead>
                <tbody>
                    ${itemsHtml}
                </tbody>
            </table>

            <div class="receipt-divider-dashed"></div>

            <div class="receipt-totals-box">
                <div class="total-row">
                    <span>Subtotal:</span>
                    <span>${formatCurrency(bill.subtotal)}</span>
                </div>
                ${discountRow}
                <div class="total-row">
                    <span>CGST (2.5%):</span>
                    <span>${formatCurrency(cgst)}</span>
                </div>
                <div class="total-row">
                    <span>SGST (2.5%):</span>
                    <span>${formatCurrency(sgst)}</span>
                </div>

                <div class="receipt-divider-solid"></div>

                <div class="total-row grand-total-row">
                    <span>GRAND TOTAL:</span>
                    <span class="grand-total-price">${formatCurrency(bill.grand_total)}</span>
                </div>

                <div class="receipt-divider-solid"></div>
            </div>

            <div class="receipt-qr-section">
                <div class="qr-mockup">
                    <i class="fa-solid fa-qrcode fa-3x"></i>
                </div>
                <p class="qr-label">Scan to verify invoice / UPI Record</p>
            </div>

            <div class="receipt-barcode">
                <div class="barcode-lines"></div>
                <span class="barcode-digits">${bill.invoice_number}</span>
            </div>

            <div class="receipt-footer">
                <p class="thank-you-msg">Thank You for Your Visit!</p>
                <p>Fresh Food &bull; Quick Service &bull; Great Taste</p>
                <p class="footer-note">Goods once sold cannot be returned without bill.</p>
            </div>

            <div class="receipt-sawtooth-bottom"></div>
        </div>
    `;
}

function printModalReceipt() {
    const printContent = document.getElementById('receiptModalBody');
    if (!printContent) return;

    const printWin = window.open('', '', 'width=600,height=800');
    printWin.document.write(`
        <html>
            <head>
                <title>Print Receipt</title>
                <link rel="stylesheet" href="/static/css/receipt.css">
                <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@600;800&display=swap" rel="stylesheet">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
                <style>
                    body {
                        margin: 0;
                        padding: 10px;
                        display: flex;
                        justify-content: center;
                    }
                    .thermal-receipt {
                        box-shadow: none;
                        max-width: 80mm;
                        width: 80mm;
                    }
                </style>
            </head>
            <body>
                ${printContent.innerHTML}
                <script>
                    window.onload = function() {
                        window.print();
                        window.onafterprint = function() { window.close(); };
                    };
                </script>
            </body>
        </html>
    `);
    printWin.document.close();
}

// Close modal on Escape key or backdrop click
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeReceiptModal();
    }
});

const receiptModalOverlay = document.getElementById('receiptModal');
if (receiptModalOverlay) {
    receiptModalOverlay.addEventListener('click', (e) => {
        if (e.target === receiptModalOverlay) {
            closeReceiptModal();
        }
    });
}
