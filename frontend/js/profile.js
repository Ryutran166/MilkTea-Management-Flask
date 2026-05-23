async function getProfile() {

    const token = localStorage.getItem(
        "access_token"
    );

    const response = await fetch(
        "/auth/profile",
        {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    const data = await response.json();

    if (!response.ok) {

        alert(data.message);

        window.location.href = "./login.html";

        return;
    }

    document.getElementById("profile-data").innerHTML = `
        <p><strong>ID:</strong> ${data.id}</p>
        <p><strong>Username:</strong> ${data.username}</p>
        <p><strong>Role:</strong> ${data.role}</p>
    `;
}


async function logout() {

    const refresh_token = localStorage.getItem(
        "refresh_token"
    );

    await fetch(
        "/auth/logout",
        {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${refresh_token}`
            }
        }
    );

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    window.location.href = "./login.html";
}

function goToRoleTest() {
    window.location.href = "./role-test.html";
}

getProfile();
