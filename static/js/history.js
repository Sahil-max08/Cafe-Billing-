/**
 * History Page Module
 */

class HistoryManager {
    constructor() {
        this.init();
    }

    init() {
        // Any specific history page bindings
    }

    exportToCSV() {
        const table = document.getElementById('historyTable');
        if (!table) return;

        let csv = [];
        const rows = table.querySelectorAll('tr');

        for (let i = 0; i < rows.length; i++) {
            const row = [];
            const cols = rows[i].querySelectorAll('th, td');

            // Skip last column (Actions)
            for (let j = 0; j < cols.length - 1; j++) {
                let text = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, ' ').replace(/\s+/g, ' ').trim();
                text = text.replace(/"/g, '""');
                row.push('"' + text + '"');
            }

            if (row.length > 0) {
                csv.push(row.join(','));
            }
        }

        const csvContent = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv.join('\n'));
        const link = document.createElement('a');
        const filename = `Cafeteria_Billing_System_Invoices_${new Date().toISOString().slice(0, 10)}.csv`;

        link.setAttribute('href', csvContent);
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showToast('Invoices exported to CSV file.', 'success');
    }
}

let historyApp;
document.addEventListener('DOMContentLoaded', () => {
    historyApp = new HistoryManager();
});
