// messages.js – updated to avoid forced reflow
document.addEventListener("DOMContentLoaded", () => {
  // Auto-dismiss messages after 3 seconds (Tailwind-only)
  setTimeout(() => {
    document.querySelectorAll(".message-item").forEach((message) => {
      message.classList.remove("opacity-100", "translate-y-0");
      message.classList.add("opacity-0", "-translate-y-2");

      setTimeout(() => {
        message.remove();
      }, 500); // matches duration-500
    });
  }, 3000);

  // Confirmation dialog function
  window.showConfirmation = function (message, onConfirm) {
    const container = document.createElement("div");
    container.className =
      "fixed inset-0 bg-[color:var(--color-brand-dark)]/50 flex items-center justify-center z-50";
    container.setAttribute("role", "dialog");
    container.setAttribute("aria-modal", "true");
    container.setAttribute("aria-label", "Confirmation dialog");

    const dialog = document.createElement("div");
    dialog.className =
      "bg-[color:var(--color-brand-light)] rounded-2xl p-6 max-w-sm mx-auto shadow-xl border border-[color:var(--color-brand-accent)]";

    const messageEl = document.createElement("div");
    messageEl.className = "mb-4 text-[color:var(--color-font-main)]";
    messageEl.textContent = message;

    const buttonContainer = document.createElement("div");
    buttonContainer.className = "flex justify-end gap-3";

    const confirmButton = document.createElement("button");
    confirmButton.className =
      "px-4 py-2 bg-[color:var(--color-brand-primary)] text-[color:var(--color-font-main)] rounded hover:bg-[color:var(--color-brand-dark)] transition-colors";
    confirmButton.textContent = "OK";
    confirmButton.onclick = () => {
      container.remove();
      if (onConfirm) onConfirm();
    };

    const cancelButton = document.createElement("button");
    cancelButton.className =
      "px-4 py-2 bg-[color:var(--color-brand-light)] text-[color:var(--color-font-main)] border border-[color:var(--color-brand-accent)] rounded hover:bg-[color:var(--color-brand-secondary)] hover:text-[color:var(--color-font-main)] transition-colors";
    cancelButton.textContent = "Cancel";
    cancelButton.onclick = () => container.remove();

    buttonContainer.appendChild(cancelButton);
    buttonContainer.appendChild(confirmButton);

    dialog.appendChild(messageEl);
    dialog.appendChild(buttonContainer);
    container.appendChild(dialog);
    document.body.appendChild(container);

    confirmButton.focus();
  };
});
