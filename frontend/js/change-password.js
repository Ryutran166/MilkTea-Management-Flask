async function changePassword() {
    const token = localStorage.getItem("access_token");

    const old_password = document.getElementById("old_password").value;
    const new_password = document.getElementById("new_password").value;
    const confirm_password = document.getElementById("confirm_password").value;

    const response = await fetch(
        "/auth/change-password",
        {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                old_password,
                new_password,
                confirm_password
            })
        }
    );

    const data = await response.json();
    const msgEl = document.getElementById("change-password-message");

    if (!response.ok) {
        msgEl.style.color = "#b00020";
        msgEl.innerText = data.message || "Failed to change password";
        return;
    }

    msgEl.style.color = "#1b5e20";
    msgEl.innerText = data.message || "Password changed successfully";

    // Clear inputs
    document.getElementById("old_password").value = "";
    document.getElementById("new_password").value = "";
    document.getElementById("confirm_password").value = "";
}

