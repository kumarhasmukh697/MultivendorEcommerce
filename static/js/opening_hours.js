class OpeningHoursManager {
    constructor() {
        this.form = document.getElementById('add-opening-hour-form');
        this.table = document.getElementById('hours-table');
        this.isClosedCheckbox = document.getElementById('is_closed');
        this.timeInputs = {
            opening: document.getElementById('opening_time'),
            closing: document.getElementById('closing_time')
        };
        
        this.init();
    }

    init() {
        // Initialize event listeners
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.table.addEventListener('click', (e) => this.handleDelete(e));
        this.isClosedCheckbox.addEventListener('change', () => this.toggleTimeInputs());
        
        // Initial state of time inputs
        this.toggleTimeInputs();
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = {
            day: this.form.day.value,
            opening_time: this.isClosedCheckbox.checked ? null : this.timeInputs.opening.value,
            closing_time: this.isClosedCheckbox.checked ? null : this.timeInputs.closing.value,
            is_closed: this.isClosedCheckbox.checked
        };

        try {
            const response = await this.sendRequest('/vendor/ajax/add-opening-hour/', 'POST', formData);
            if (response.success) {
                await this.refreshTable();
                this.form.reset();
                this.showAlert('Success! Opening hours added.', 'success');
            } else {
                this.showAlert(response.error || 'Failed to add opening hours.', 'error');
            }
        } catch (error) {
            this.showAlert('An error occurred.', 'error');
        }
    }

    async handleDelete(e) {
        if (!e.target.matches('.delete-hour')) return;
        
        if (!confirm('Are you sure you want to delete these hours?')) return;

        const id = e.target.dataset.id;
        try {
            const response = await this.sendRequest('/vendor/ajax/delete-opening-hour/', 'POST', { id });
            if (response.success) {
                await this.refreshTable();
                this.showAlert('Opening hours deleted successfully.', 'success');
            } else {
                this.showAlert('Failed to delete opening hours.', 'error');
            }
        } catch (error) {
            this.showAlert('An error occurred.', 'error');
        }
    }

    async refreshTable() {
        try {
            const response = await fetch('/vendor/opening_hours/?ajax=1');
            const data = await response.json();
            this.updateTableContent(data.hours_status);
        } catch (error) {
            console.error('Failed to refresh table:', error);
        }
    }

    updateTableContent(hoursStatus) {
        const tbody = this.table.querySelector('tbody');
        tbody.innerHTML = hoursStatus.map(h => this.createTableRow(h)).join('');
    }

    createTableRow(hour) {
        return `
            <tr data-id="${hour.id || ''}">
                <td>${hour.day}</td>
                <td>${hour.opening_time ? hour.opening_time.substring(0,5) : '-'}</td>
                <td>${hour.closing_time ? hour.closing_time.substring(0,5) : '-'}</td>
                <td>${this.getStatusBadge(hour.status)}</td>
                <td>${hour.id ? 
                    `<button class="btn btn-danger btn-sm delete-hour" data-id="${hour.id}">
                        <i class="fas fa-trash"></i> Delete
                    </button>` : 
                    ''}
                </td>
            </tr>
        `;
    }

    getStatusBadge(status) {
        const badges = {
            'Shop Open': 'success',
            'Closed': 'danger',
            'Holiday': 'warning text-dark',
            'default': 'secondary'
        };
        const badgeType = badges[status] || badges.default;
        return `<span class="badge bg-${badgeType}">${status}</span>`;
    }

    toggleTimeInputs() {
        const disabled = this.isClosedCheckbox.checked;
        this.timeInputs.opening.disabled = disabled;
        this.timeInputs.closing.disabled = disabled;
        if (disabled) {
            this.timeInputs.opening.value = '';
            this.timeInputs.closing.value = '';
        }
    }

    async sendRequest(url, method, data) {
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        return response.json();
    }

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        this.form.parentElement.insertBefore(alertDiv, this.form);
        setTimeout(() => alertDiv.remove(), 3000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new OpeningHoursManager();
});