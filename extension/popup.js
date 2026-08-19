const API_URL = "http://127.0.0.1:8000/predict";


// ==========================================
// Get elements from popup
// ==========================================

const urlElement = document.getElementById("url");

const resultElement = document.getElementById("result");

const riskElement = document.getElementById("risk");

const statusIconElement =
    document.getElementById("status-icon");

const phishingProbabilityElement =
    document.getElementById("phishing-probability");

const phishingBarElement =
    document.getElementById("phishing-bar");

const scanButton =
    document.getElementById("scan-button");


// ==========================================
// Get current browser tab
// ==========================================

async function getCurrentTab() {

    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    return tabs[0];
}


// ==========================================
// Scan URL
// ==========================================

async function scanURL() {

    try {

        // Show loading state

        statusIconElement.textContent = "🔍";

        resultElement.textContent = "Scanning...";

        riskElement.innerHTML =
            '<span class="loading">Analyzing URL...</span>';

        phishingProbabilityElement.textContent =
            "0%";

        phishingBarElement.style.width = "0%";


        // Get current tab

        const tab = await getCurrentTab();

        const url = tab.url;


        // Display URL

        urlElement.textContent = url;


        // Check whether URL is available
        if (!url) {
            throw new Error("Could not read the current URL.");
        }

        // ======================================
        // Handle Internal Browser Pages (edge://, chrome://, about:, etc.)
        // ======================================
        const isInternalPage = (
            url.startsWith("edge://") ||
            url.startsWith("chrome://") ||
            url.startsWith("about:") ||
            url.startsWith("brave://") ||
            url.startsWith("opera://") ||
            url.startsWith("chrome-extension://") ||
            url.startsWith("edge-extension://") ||
            url.startsWith("file://") ||
            url.startsWith("devtools://") ||
            url.startsWith("view-source:")
        );

        if (isInternalPage) {
            statusIconElement.textContent = "🛡️";
            resultElement.textContent = "BROWSER SYSTEM PAGE";
            riskElement.innerHTML = '<span style="color: #10b981; font-weight: 600;">SAFE (Internal Page)</span>';
            phishingProbabilityElement.textContent = "0%";
            phishingBarElement.style.width = "0%";
            return;
        }

        // ======================================
        // Send URL to FastAPI backend
        // ======================================
        const response = await fetch(
            API_URL,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    url: url
                })
            }
        );



        // Check HTTP response

        if (!response.ok) {

            throw new Error(
                "Backend returned HTTP " +
                response.status
            );

        }


        // Convert response to JSON

        const data = await response.json();


        // ======================================
        // Display prediction
        // ======================================

        const phishingProbability =
            data.phishing_probability;


        phishingProbabilityElement.textContent =
            phishingProbability + "%";


        phishingBarElement.style.width =
            phishingProbability + "%";


        // ======================================
        // Display result
        // ======================================

        if (data.result === "PHISHING") {

            statusIconElement.textContent = "🚨";

            resultElement.textContent =
                "POSSIBLE PHISHING";

            riskElement.innerHTML =
                '<strong>HIGH RISK</strong>';

        }

        else {

            statusIconElement.textContent = "🛡️";

            resultElement.textContent =
                "LIKELY LEGITIMATE";

            riskElement.innerHTML =
                "Risk: <strong>" +
                data.risk +
                "</strong>";

        }

    }

    catch (error) {

        console.error(error);

        statusIconElement.textContent = "⚠️";

        resultElement.textContent =
            "Scan failed";

        riskElement.innerHTML =
            '<span class="error">' +
            error.message +
            "</span>";

    }

}


// ==========================================
// Scan Again button
// ==========================================

scanButton.addEventListener(
    "click",
    scanURL
);


// ==========================================
// Automatically scan when popup opens
// ==========================================

scanURL();