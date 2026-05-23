const resultEl = document.getElementById("test-result");

const testCases = [
    { name: "/admin-only", endpoint: "/admin-only" },
    { name: "/manager-only", endpoint: "/manager-only" },
    { name: "/staff-admin", endpoint: "/staff-admin" }
];

function appendResult(name, ok, message, status) {
    const line = document.createElement("p");
    line.textContent = `${name} -> ${ok ? "PASS" : "FAIL"} (${status}): ${message}`;
    line.style.color = ok ? "#2e7d32" : "#c62828";
    resultEl.appendChild(line);
}

async function runSingleTest(testCase) {
    const token = localStorage.getItem("access_token");

    if (!token) {
        appendResult(testCase.name, false, "Missing access token, please login", 401);
        return;
    }

    try {
        const response = await fetch(testCase.endpoint, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const data = await response.json();
        const message = data.message || "No message";
        appendResult(testCase.name, response.ok, message, response.status);
    }
    catch (error) {
        appendResult(testCase.name, false, "Cannot connect to server", 0);
    }
}

async function runAllTests() {
    resultEl.innerHTML = "";
    for (const testCase of testCases) {
        await runSingleTest(testCase);
    }
}

document.getElementById("testAdminBtn").addEventListener("click", async () => {
    resultEl.innerHTML = "";
    await runSingleTest(testCases[0]);
});

document.getElementById("testManagerBtn").addEventListener("click", async () => {
    resultEl.innerHTML = "";
    await runSingleTest(testCases[1]);
});

document.getElementById("testStaffAdminBtn").addEventListener("click", async () => {
    resultEl.innerHTML = "";
    await runSingleTest(testCases[2]);
});

document.getElementById("testAllBtn").addEventListener("click", runAllTests);

document.getElementById("backProfileBtn").addEventListener("click", () => {
    window.location.href = "./profile.html";
});
