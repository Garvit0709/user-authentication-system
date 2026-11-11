
const message = document.getElementById("message");

function showMessage(text) {
    if (message) {
        message.textContent = text;
    }
}

async function sendRequest(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "same-origin",
        body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || result.msg || "Request failed");
    }

    return result;
}

// Registration
const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const data = {
            username: document.getElementById("username").value.trim(),
            email: document.getElementById("email").value.trim(),
            password: document.getElementById("password").value
        };

        const button = registerForm.querySelector("button");
        button.disabled = true;

        try {
            await sendRequest("/api/auth/register", data);
            showMessage("Registration successful. Redirecting to login...");

            window.location.href = "/login";
        } catch (error) {
            showMessage(error.message);
        } finally {
            button.disabled = false;
        }
    });
}

// Login
const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const data = {
            email: document.getElementById("email").value.trim(),
            password: document.getElementById("password").value
        };

        const button = loginForm.querySelector("button");
        button.disabled = true;

        try {
            await sendRequest("/api/auth/login", data);
            window.location.href = "/dashboard";
        } catch (error) {
            showMessage(error.message);
        } finally {
            button.disabled = false;
        }
    });
}

// Read CSRF cookie for logout
function getCookie(name) {
    const cookies = document.cookie.split("; ");

    for (const cookie of cookies) {
        const [key, ...value] = cookie.split("=");

        if (key === name) {
            return decodeURIComponent(value.join("="));
        }
    }

    return null;
}

// Dashboard
const profile = document.getElementById("profile");

if (profile) {
    async function loadProfile() {
        try {
            const response = await fetch("/api/auth/profile", {
                credentials: "same-origin",
                cache: "no-store"
            });

            if (!response.ok) {
                window.location.replace("/login");
                return;
            }

            const user = await response.json();

            document.getElementById("username").textContent = user.username;
            document.getElementById("userEmail").textContent = user.email;

            profile.hidden = false;
            showMessage("");

        } catch (error) {
            showMessage("Unable to load profile.");
        }
    }

    loadProfile();

    document.getElementById("logoutBtn").addEventListener("click", async function() {
        const csrfToken = getCookie("csrf_access_token");

        if (!csrfToken) {
            showMessage("Session token missing. Please log in again.");
            return;
        }

        const button = this;
        button.disabled = true;

        try {
            const response = await fetch("/api/auth/logout", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-CSRF-TOKEN": csrfToken
                }
            });

            if (!response.ok) {
                throw new Error("Logout failed");
            }

            window.location.replace("/login");

        } catch (error) {
            showMessage(error.message);
            button.disabled = false;
        }
    });
}
