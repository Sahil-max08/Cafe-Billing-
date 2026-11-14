/**
 * Sales Analytics & Reports Module with Chart.js
 */

document.addEventListener('DOMContentLoaded', () => {
    initReportCharts();
    initPrintTimestamp();
});

function initPrintTimestamp() {
    const el = document.querySelector('.auto-print-timestamp');
    if (el) {
        const now = new Date();
        el.textContent = now.toLocaleDateString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    }
}

function initReportCharts() {
    const dataEl = document.getElementById('reportJsonData');
    if (!dataEl) return;

    let reportData;
    try {
        reportData = JSON.parse(dataEl.textContent);
    } catch (e) {
        console.error('Error parsing report json:', e);
        return;
    }

    if (!reportData) return;

    // 1. Revenue & Orders Trend Chart
    const trendCtx = document.getElementById('revenueTrendChart')?.getContext('2d');
    if (trendCtx) {
        const trends = reportData.daily_trends || [];
        const labels = trends.map(t => t.sale_date);
        const revenues = trends.map(t => t.daily_revenue);
        const orders = trends.map(t => t.order_count);

        // Fallback if empty
        if (labels.length === 0) {
            labels.push('Today');
            revenues.push(reportData.total_revenue || 0);
            orders.push(reportData.total_orders || 0);
        }

        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Revenue (₹)',
                        data: revenues,
                        borderColor: '#ea580c',
                        backgroundColor: 'rgba(234, 88, 12, 0.12)',
                        borderWidth: 2.5,
                        fill: true,
                        tension: 0.35,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Orders Count',
                        data: orders,
                        borderColor: '#0f766e',
                        backgroundColor: 'rgba(15, 118, 110, 0.1)',
                        borderWidth: 2,
                        borderDash: [4, 4],
                        tension: 0.2,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { font: { family: 'Inter', size: 12 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (context.dataset.yAxisID === 'y') {
                                    return ` Revenue: ₹${context.raw.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
                                }
                                return ` Orders: ${context.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        ticks: {
                            callback: function(value) { return '₹' + value; }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }

    // 2. Category Share Chart
    const catCtx = document.getElementById('categoryChart')?.getContext('2d');
    if (catCtx) {
        const catData = reportData.category_sales || [];
        const labels = catData.map(c => c.category);
        const values = catData.map(c => c.category_sales);

        new Chart(catCtx, {
            type: 'doughnut',
            data: {
                labels: labels.length ? labels : ['No Category Data'],
                datasets: [{
                    data: values.length ? values : [1],
                    backgroundColor: [
                        '#f59e0b', // Snacks
                        '#ea580c', // Meals
                        '#0284c7', // Beverages
                        '#db2777', // Desserts
                        '#10b981'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, font: { family: 'Inter', size: 11 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                return ` ₹${ctx.raw.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
                            }
                        }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 3. Payment Methods Chart
    const payCtx = document.getElementById('paymentChart')?.getContext('2d');
    if (payCtx) {
        const payData = reportData.payment_methods || [];
        const labels = payData.map(p => p.payment_method);
        const values = payData.map(p => p.total_amount);

        new Chart(payCtx, {
            type: 'doughnut',
            data: {
                labels: labels.length ? labels : ['No Payment Data'],
                datasets: [{
                    data: values.length ? values : [1],
                    backgroundColor: [
                        '#10b981', // Cash
                        '#3b82f6', // UPI
                        '#8b5cf6'  // Card
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, font: { family: 'Inter', size: 11 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                return ` ₹${ctx.raw.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
                            }
                        }
                    }
                },
                cutout: '68%'
            }
        });
    }
}
