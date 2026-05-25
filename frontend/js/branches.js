function setMessage(msg, isError = false) {
    const el = document.getElementById("branches-message");
    if (!el) return;
    el.innerText = msg;
    el.style.color = isError ? "red" : "green";
}

function getToken() {
    return localStorage.getItem("access_token");
}

async function fetchBranches() {
    const token = getToken();

    const res = await fetch("/branches", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
        throw new Error(data.message || "Failed to load branches");
    }

    return data.data || [];
}

function escapeHtml(s) {
    if (s === null || s === undefined) return "";
    return String(s)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function renderBranches(branches) {
    const tbody = document.querySelector("#branches-table tbody");
    tbody.innerHTML = "";

    branches.forEach((b) => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${b.id}</td>
            <td>${b.name ?? ""}</td>
            <td>${b.phone ?? ""}</td>
            <td>${b.address ?? ""}</td>
            <td>${b.status ? "Active" : "Inactive"}</td>
            <td>
                <button style="width:auto;" onclick="prefillEdit(${b.id}, '${escapeHtml(b.name)}', '${escapeHtml(b.phone)}', '${escapeHtml(b.address)}', ${b.status})">Sửa</button>
                <button style="width:auto; background:#d9534f;" onclick="deleteBranch(${b.id})">Xoá</button>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

async function prefillEdit(id, name, phone, address, status) {
    document.getElementById("edit-id").value = id;
    document.getElementById("edit-name").value = name;
    document.getElementById("edit-phone").value = phone;
    document.getElementById("edit-address").value = address;
    document.getElementById("edit-status").value = String(status);
}

async function createBranch() {
    const token = getToken();

    const name = document.getElementById("create-name").value.trim();
    const phone = document.getElementById("create-phone").value.trim();
    const address = document.getElementById("create-address").value.trim();
    const status = document.getElementById("create-status").value === "true";

    if (!name) {
        setMessage("Tên chi nhánh không được trống", true);
        return;
    }

    const res = await fetch("/branches", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
            name,
            phone: phone || null,
            address: address || null,
            status
        })
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
        setMessage(data.message || "Create failed", true);
        return;
    }

    setMessage("Tạo chi nhánh thành công");

    document.getElementById("create-name").value = "";
    document.getElementById("create-phone").value = "";
    document.getElementById("create-address").value = "";

    await load();
}

async function updateBranch() {
    const token = getToken();

    const id = parseInt(document.getElementById("edit-id").value, 10);
    if (!id) {
        setMessage("Vui lòng nhập Branch ID", true);
        return;
    }

    const nameRaw = document.getElementById("edit-name").value.trim();
    const phoneRaw = document.getElementById("edit-phone").value.trim();
    const addressRaw = document.getElementById("edit-address").value.trim();
    const status = document.getElementById("edit-status").value === "true";

    const body = {
        name: nameRaw || undefined,
        phone: phoneRaw || null,
        address: addressRaw || null,
        status
    };

    Object.keys(body).forEach((k) => {
        if (body[k] === undefined) delete body[k];
    });

    const res = await fetch(`/branches/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(body)
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
        setMessage(data.message || "Update failed", true);
        return;
    }

    setMessage("Cập nhật thành công");
    await load();
}

async function deleteBranch(id) {
    const token = getToken();

    if (!confirm(`Xoá chi nhánh #${id}?`)) return;

    const res = await fetch(`/branches/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
        setMessage(data.message || "Delete failed", true);
        return;
    }

    setMessage("Xoá thành công");
    await load();
}

async function logout() {
    const refresh_token = localStorage.getItem("refresh_token");

    await fetch("/auth/logout", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${refresh_token}`
        }
    });

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    window.location.href = "./login.html";
}

function goBackProfile() {
    window.location.href = "./profile.html";
}

async function load() {
    try {
        setMessage("Đang tải...");
        const branches = await fetchBranches();
        renderBranches(branches);
        setMessage("");
    } catch (e) {
        setMessage(e.message || "Error", true);

        const msg = String(e.message || "").toLowerCase();
        if (msg.includes("token") || msg.includes("401")) {
            window.location.href = "./login.html";
        }
    }
}

load();

