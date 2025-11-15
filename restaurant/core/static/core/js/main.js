// JavaScript para funcionalidades adicionales

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });

    // Confirmación para acciones importantes
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que quieres realizar esta acción?')) {
                e.preventDefault();
            }
        });
    });

    // Mejorar la experiencia de los dropdowns
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('show.bs.dropdown', function() {
            this.querySelector('.dropdown-toggle').classList.add('active');
        });
        
        dropdown.addEventListener('hide.bs.dropdown', function() {
            this.querySelector('.dropdown-toggle').classList.remove('active');
        });
    });

    // Smooth scroll para anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Mejorar la experiencia en móviles
    if (window.innerWidth < 768) {
        document.body.classList.add('mobile-view');
    }

    // Actualizar automáticamente el dashboard cada 30 segundos (solo en dashboards)
    if (window.location.pathname.includes('dashboard')) {
        setInterval(() => {
            window.location.reload();
        }, 30000);
    }
});

// Función para formatear moneda
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas 
                ${type === 'success' ? 'fa-check-circle' : 
                  type === 'error' || type === 'danger' ? 'fa-exclamation-circle' : 
                  type === 'warning' ? 'fa-exclamation-triangle' : 
                  'fa-info-circle'} 
                me-2"></i>
            <div>${message}</div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Función para cargar contenido dinámicamente
async function loadContent(url, container) {
    try {
        const response = await fetch(url);
        const html = await response.text();
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading content:', error);
        showNotification('Error al cargar el contenido', 'error');
    }
}

// Utilidad para formatear fechas
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('es-ES', options);
}