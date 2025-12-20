document.addEventListener("DOMContentLoaded", function () {

  const buttons = document.querySelectorAll(".favourite-btn");

  buttons.forEach(button => {
    button.addEventListener("click", function (e) {
      e.preventDefault();

      const originalHTML = this.innerHTML;
      const actionUrl = this.dataset.actionUrl;
      const csrfToken = this.dataset.csrf;

      this.innerHTML = "⏳ Saving...";
      this.disabled = true;

      const formData = new FormData();
      formData.append("csrfmiddlewaretoken", csrfToken);

      fetch(actionUrl, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then(response => {
          const contentType = response.headers.get("content-type");
          if (!response.ok || !contentType?.includes("application/json")) {
            throw new Error("Invalid response");
          }
          return response.json();
        })
        .then(data => {
          if (data.status === "success") {

            // Update button state and show toast
            if (data.is_favourite) {
              this.innerHTML = "❤️ Remove from Wish List";
              this.classList.add("bg-red-50", "border-red-300");
              this.classList.remove("bg-white");
              showToast("Added to your wish list");
            } else {
              this.innerHTML = "🤍 Add to Wish List";
              this.classList.remove("bg-red-50", "border-red-300");
              this.classList.add("bg-white");
              showToast("Removed from your wish list");
            }

          } else if (data.status === "unauthenticated") {
            window.location.href = data.redirect_url;
          } else {
            this.innerHTML = originalHTML;
          }
        })
        .catch(error => {
          console.error("Wishlist error:", error);
          this.innerHTML = originalHTML;
        })
        .finally(() => {
          this.disabled = false;
        });
    });
  });

});
