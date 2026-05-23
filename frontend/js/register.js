const registerForm = document.getElementById("registerForm");
const messageEl = document.getElementById("message");

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const full_name = document.getElementById("full_name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;

    messageEl.innerText = "";

    try {
        const response = await fetch("/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                full_name,
                phone,
                username,
                password,
                role
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            messageEl.innerText = data.message || "Register failed";
            return;
        }

        messageEl.style.color = "#2e7d32";
        messageEl.innerText = "Register successful. Redirecting to login...";
        setTimeout(() => {
            window.location.href = "./login.html";
        }, 1000);
    }
    catch (error) {
        messageEl.innerText = "Cannot connect to server";
    }
});
