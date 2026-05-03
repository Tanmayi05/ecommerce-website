document.addEventListener("DOMContentLoaded", function () {
    const wishlist = JSON.parse(localStorage.getItem("wishlist")) || {};
    updateWishlistBadge();

    // Attach heart icon buttons to product cards dynamically
    document.querySelectorAll(".product-card").forEach(card => {
        const id = card.dataset.id;
        const name = card.dataset.name;
        const price = card.dataset.price;

        // Create heart button only if it doesn't exist
        if (!card.querySelector(".wishlist-icon")) {
            const heartBtn = document.createElement("button");
            heartBtn.className = "wishlist-icon";
            heartBtn.style.fontSize = "20px";
            heartBtn.style.border = "none";
            heartBtn.style.background = "transparent";
            heartBtn.style.cursor = "pointer";
            heartBtn.style.position = "absolute";
            heartBtn.style.top = "10px";
            heartBtn.style.right = "10px";

            heartBtn.addEventListener("click", function () {
                toggleWishlist(id, name, price, heartBtn);
            });

            card.style.position = "relative"; // To position heart button inside
            card.appendChild(heartBtn);
        }

        // Update heart icon appearance
        const heartBtn = card.querySelector(".wishlist-icon");
        updateHeartIcon(id, heartBtn);
    });

    function toggleWishlist(id, name, price, btn) {
        if (wishlist[id]) {
            delete wishlist[id];
        } else {
            wishlist[id] = { id, name, price };
        }
        localStorage.setItem("wishlist", JSON.stringify(wishlist));
        updateHeartIcon(id, btn);
        updateWishlistBadge();
    }

    function updateHeartIcon(id, btn) {
        if (wishlist[id]) {
            btn.innerHTML = "♥";
            btn.style.color = "red";
        } else {
            btn.innerHTML = "♡";
            btn.style.color = "gray";
        }
    }

    function updateWishlistBadge() {
        const badge = document.getElementById("wishlist-badge");
        if (badge) {
            badge.textContent = Object.keys(wishlist).length;
        }
    }
});