function confirmDelete(username) {
    return window.confirm(`Delete ${username}'s stored FitBuddy data?`);
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#plan-form");
    if (!form) return;

    form.addEventListener("submit", () => {
        const button = form.querySelector("button[type='submit']");
        if (button) {
            button.disabled = true;
            button.innerHTML = "Generating plan…";
        }
    });
});
