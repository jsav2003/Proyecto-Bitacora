// ========================================
// BITÁCORA CIENTÍFICA - JAVASCRIPT PERSONALIZADO
// ========================================

// Esperar a que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // INICIALIZACIÓN DE DATATABLES
    // ========================================
    if ($.fn.DataTable) {
        $('.table-datatable').DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
            },
            responsive: true,
            pageLength: 10,
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rtip',
            order: [[0, 'desc']],
            columnDefs: [
                {
                    targets: -1,
                    orderable: false,
                    searchable: false
                }
            ]
        });
    }

    // ========================================
    // AUTO-HIDE MENSAJES
    // ========================================
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // ========================================
    // PREVIEW DE IMÁGENES
    // ========================================
    const imageInput = document.getElementById('id_imagen');
    const imagePreview = document.getElementById('imagePreview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                // Validar tipo de archivo
                const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Archivo inválido',
                        text: 'Por favor selecciona una imagen válida (JPG, PNG, GIF)',
                        confirmButtonColor: '#198754'
                    });
                    imageInput.value = '';
                    imagePreview.style.display = 'none';
                    return;
                }
                
                // Validar tamaño (máximo 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Archivo muy grande',
                        text: 'La imagen no debe superar los 5MB',
                        confirmButtonColor: '#198754'
                    });
                    imageInput.value = '';
                    imagePreview.style.display = 'none';
                    return;
                }
                
                // Mostrar preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                    imagePreview.classList.add('show');
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.style.display = 'none';
                imagePreview.classList.remove('show');
            }
        });
    }

    // ========================================
    // CONFIRMACIÓN DE ELIMINACIÓN CON SWEETALERT2
    // ========================================
    const deleteButtons = document.querySelectorAll('.btn-delete');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('href');
            const itemName = this.getAttribute('data-name') || 'este registro';
            
            Swal.fire({
                title: '¿Estás seguro?',
                html: `Vas a eliminar: <strong>${itemName}</strong>`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar',
                reverseButtons: true,
                focusCancel: true
            }).then((result) => {
                if (result.isConfirmed) {
                    // Mostrar loading
                    Swal.fire({
                        title: 'Eliminando...',
                        text: 'Por favor espera',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        showConfirmButton: false,
                        willOpen: () => {
                            Swal.showLoading();
                        }
                    });
                    
                    // Redirigir a la URL de eliminación
                    window.location.href = url;
                }
            });
        });
    });

    // ========================================
    // TOOLTIPS DE BOOTSTRAP
    // ========================================
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // ========================================
    // VALIDACIÓN DE FORMULARIOS
    // ========================================
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Mostrar alerta de validación
                Swal.fire({
                    icon: 'error',
                    title: 'Formulario incompleto',
                    text: 'Por favor completa todos los campos requeridos correctamente',
                    confirmButtonColor: '#198754'
                });
            }
            
            form.classList.add('was-validated');
        }, false);
    });

    // ========================================
    // NÚMEROS ANIMADOS (CONTADOR)
    // ========================================
    const animateCounter = (element) => {
        const target = parseInt(element.getAttribute('data-target'));
        const duration = 2000; // 2 segundos
        const increment = target / (duration / 16); // 60 FPS
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                element.textContent = Math.ceil(current);
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target;
            }
        };
        
        updateCounter();
    };

    // Animar contadores en la página de inicio
    const counters = document.querySelectorAll('.stats-number[data-target]');
    if (counters.length > 0) {
        // Observer para animar solo cuando sea visible
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        counters.forEach(counter => observer.observe(counter));
    }

    // ========================================
    // BÚSQUEDA EN TIEMPO REAL (para listas sin DataTables)
    // ========================================
    const searchInput = document.getElementById('searchInput');
    const searchableTable = document.getElementById('searchableTable');
    
    if (searchInput && searchableTable) {
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const rows = searchableTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }

    // ========================================
    // ZOOM EN THUMBNAILS
    // ========================================
    const thumbnails = document.querySelectorAll('.img-thumbnail-custom');
    
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            const src = this.src;
            const alt = this.alt;
            
            Swal.fire({
                imageUrl: src,
                imageAlt: alt,
                imageWidth: '100%',
                imageHeight: 'auto',
                showCloseButton: true,
                showConfirmButton: false,
                customClass: {
                    image: 'img-fluid'
                }
            });
        });
    });

    // ========================================
    // SMOOTH SCROLL PARA ANCHORS
    // ========================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // ========================================
    // ACTUALIZAR AÑO EN FOOTER
    // ========================================
    const yearElement = document.getElementById('currentYear');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }

    // ========================================
    // LOADING SPINNER EN FORMULARIOS
    // ========================================
    const submitButtons = document.querySelectorAll('form button[type="submit"]');
    
    submitButtons.forEach(button => {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                button.disabled = true;
                const originalText = button.innerHTML;
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
                
                // Restaurar después de 3 segundos (por si hay errores)
                setTimeout(() => {
                    button.disabled = false;
                    button.innerHTML = originalText;
                }, 3000);
            });
        }
    });

    // ========================================
    // CONFIRMACIÓN ANTES DE SALIR (si hay cambios)
    // ========================================
    let formChanged = false;
    const formInputs = document.querySelectorAll('form input, form select, form textarea');
    
    formInputs.forEach(input => {
        input.addEventListener('change', () => {
            formChanged = true;
        });
    });
    
    window.addEventListener('beforeunload', (e) => {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = '¿Estás seguro de salir? Los cambios no guardados se perderán.';
        }
    });
    
    // No mostrar confirmación al enviar formulario
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            formChanged = false;
        });
    });

    // ========================================
    // COPIAR AL PORTAPAPELES
    // ========================================
    const copyButtons = document.querySelectorAll('.btn-copy');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const text = this.getAttribute('data-copy');
            
            navigator.clipboard.writeText(text).then(() => {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'success',
                    title: 'Copiado al portapapeles',
                    showConfirmButton: false,
                    timer: 2000,
                    timerProgressBar: true
                });
            });
        });
    });

    // ========================================
    // FILTROS AVANZADOS
    // ========================================
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            const items = document.querySelectorAll('.filterable-item');
            
            // Actualizar botones activos
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filtrar items
            items.forEach(item => {
                if (filter === 'all' || item.getAttribute('data-category') === filter) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    // ========================================
    // PREVENIR DOBLE SUBMIT
    // ========================================
    document.querySelectorAll('form').forEach(form => {
        let submitted = false;
        form.addEventListener('submit', function(e) {
            if (submitted) {
                e.preventDefault();
                return false;
            }
            submitted = true;
        });
    });

    // ========================================
    // NOTIFICACIONES TOAST
    // ========================================
    window.showToast = function(message, type = 'success') {
        Swal.fire({
            toast: true,
            position: 'top-end',
            icon: type,
            title: message,
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        });
    };

    // ========================================
    // CONSOLE LOG - INFO DEL SISTEMA
    // ========================================
    console.log('%c🌱 Bitácora Científica', 'font-size: 20px; color: #198754; font-weight: bold;');
    console.log('%cSistema de gestión de experimentos de crecimiento de plantas', 'font-size: 12px; color: #6c757d;');
    console.log('%cDesarrollado con Django 5 y Bootstrap 5', 'font-size: 10px; color: #0dcaf0;');
});
