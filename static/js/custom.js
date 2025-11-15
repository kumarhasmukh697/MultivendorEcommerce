document.addEventListener('DOMContentLoaded', function() {
    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Update cart count in navbar
    function updateCartCount(count) {
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            cartCount.textContent = count;
        }
    }

    // Handle plus button
    document.querySelectorAll('.plus-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const itemId = this.getAttribute('data-item');


            fetch(`/marketplace/add-to-cart/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => { 
                document.getElementById(`quantity-${itemId}`).textContent = data.quantity;
                updateCartCount(data.cart_count);
                // Optionally reload if on cart page and quantity is 1 (item was just added)
                if (window.location.pathname.includes('/cart/') && data.quantity === 1) {
                    location.reload();
                }
            });
        });
    });


    // Handle minus button
    document.querySelectorAll('.minus-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
           
            e.preventDefault();
            const itemId = this.getAttribute('data-item');
            console.log(itemId);
            console.log(`/marketplace/remove-from-cart/${itemId}/`);

            fetch(`/marketplace/remove-from-cart/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById(`quantity-${itemId}`).textContent = data.quantity;
                updateCartCount(data.cart_count);
                // If quantity is 0, reload to remove item from cart page
                if (window.location.pathname.includes('/cart/') && data.quantity === 0) {
                    location.reload();
                }
            });
        });
    });

    // Set cart count on page load if available from backend
    if (typeof CART_COUNT_FROM_BACKEND !== 'undefined') {
        updateCartCount(CART_COUNT_FROM_BACKEND);
    }
});