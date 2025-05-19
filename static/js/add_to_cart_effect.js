document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.add-to-cart-form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new FormData(form)
            }).then(function(response) {
                if (response.ok) {
                    showCartToast();
                }
            });
        });
    });
    function showCartToast() {
        let toast = document.createElement('div');
        toast.className = 'cart-toast';
        toast.innerHTML = '<i class="fas fa-check-circle"></i> Добавлено в корзину!';
        document.body.appendChild(toast);
        setTimeout(function() { toast.classList.add('show'); }, 10);
        setTimeout(function() {
            toast.classList.remove('show');
            setTimeout(function() { toast.remove(); }, 300);
        }, 1500);
    }
});
