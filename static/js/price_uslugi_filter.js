document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const services = document.querySelectorAll('#servicesGrid .price-item');

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const filter = button.getAttribute('data-filter');

            services.forEach(service => {
                if (filter === 'all') {
                    service.style.display = 'block';
                } else {
                    if (service.classList.contains(filter)) {
                        service.style.display = 'block';
                    } else {
                        service.style.display = 'none';
                    }
                }
            });
        });
    });
});
