// ============================================
// SMART WASTE MANAGEMENT SYSTEM
// LIVE DASHBOARD SCRIPT
// ============================================

let dustbins = [];
let selectedBinId = null;
let fillChart = null;


// ============================================
// INITIALIZE DASHBOARD
// ============================================

document.addEventListener("DOMContentLoaded", () => {

    console.log("Dashboard started");

    loadDustbins();

    // Refresh every 5 seconds
    setInterval(loadDustbins, 5000);

});


// ============================================
// LOAD DUSTBINS FROM API
// ============================================

async function loadDustbins() {

    try {

        const response = await fetch("/api/dustbin");

        if (!response.ok) {
            throw new Error("API request failed");
        }

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || "Unable to load dustbins");
        }

        dustbins = result.data || [];

        console.log("Dustbins:", dustbins);

        updateDashboard();

    } catch (error) {

        console.error("Dashboard error:", error);

        showSystemError();

    }

}


// ============================================
// UPDATE EVERYTHING
// ============================================

function updateDashboard() {

    if (dustbins.length === 0) {

        updateSummary(0, 0, 0, 0);

        return;
    }

    // If no bin selected, select first bin
    if (!selectedBinId) {

        selectedBinId = dustbins[0].dustbin_id;

    }

    // Make sure selected bin still exists
    const selectedExists = dustbins.some(
        bin => bin.dustbin_id === selectedBinId
    );

    if (!selectedExists) {

        selectedBinId = dustbins[0].dustbin_id;

    }

    updateSummaryCards();

    updateDustbinSelector();

    updateSensorCards();

    updateAlerts();

    updateDustbinTable();

    updateChart();

}


// ============================================
// SUMMARY CARDS
// ============================================

function updateSummaryCards() {

    let total = dustbins.length;

    let full = 0;
    let medium = 0;
    let empty = 0;

    dustbins.forEach(bin => {

        const fill = Number(bin.fill_level || 0);

        if (fill >= 70) {

            full++;

        } else if (fill >= 30) {

            medium++;

        } else {

            empty++;

        }

    });

    updateElement("totalBins", total);
    updateElement("fullBins", full);
    updateElement("mediumBins", medium);
    updateElement("emptyBins", empty);

}


// ============================================
// SENSOR CARDS
// ============================================

function updateSensorCards() {

    const bin = dustbins.find(
        item => item.dustbin_id === selectedBinId
    );

    if (!bin) return;


    updateElement(
        "temperatureValue",
        formatNumber(bin.temperature) + " °C"
    );


    updateElement(
        "humidityValue",
        formatNumber(bin.humidity) + " %"
    );


    updateElement(
        "gasValue",
        Math.round(Number(bin.gas_raw || 0))
    );


    updateElement(
        "odorValue",
        bin.odor_status || "NORMAL"
    );


    updateElement(
        "fillValue",
        formatNumber(bin.fill_level) + " %"
    );

}


// ============================================
// SELECTOR
// ============================================

function updateDustbinSelector() {

    const selector = document.getElementById("dustbinSelector");

    if (!selector) return;


    const currentValue = selectedBinId;

    selector.innerHTML = "";


    dustbins.forEach(bin => {

        const option = document.createElement("option");

        option.value = bin.dustbin_id;

        option.textContent =
            `${bin.dustbin_id} - ${bin.location || "Unknown Location"}`;

        selector.appendChild(option);

    });


    selector.value = currentValue;


    selector.onchange = function () {

        selectedBinId = this.value;

        updateDashboard();

    };

}


// ============================================
// ALERTS
// ============================================

function updateAlerts() {

    const container =
        document.getElementById("alertsContainer");

    if (!container) return;


    container.innerHTML = "";


    let alertCount = 0;


    dustbins.forEach(bin => {

        const fill = Number(bin.fill_level || 0);

        const odor =
            String(bin.odor_status || "NORMAL").toUpperCase();


        // FULL BIN
        if (fill >= 90) {

            addAlert(
                container,
                "🚨",
                `${bin.dustbin_id} is FULL`,
                `Fill level is ${fill.toFixed(1)}%. Collection required immediately.`,
                "danger"
            );

            alertCount++;

        }

        // NEAR FULL
        else if (fill >= 70) {

            addAlert(
                container,
                "⚠️",
                `${bin.dustbin_id} is nearly full`,
                `Fill level is ${fill.toFixed(1)}%.`,
                "warning"
            );

            alertCount++;

        }


        // ODOR DANGER
        if (odor === "DANGER") {

            addAlert(
                container,
                "☠️",
                `${bin.dustbin_id} odor danger`,
                "High gas concentration detected.",
                "danger"
            );

            alertCount++;

        }


        // ODOR WARNING
        else if (odor === "WARNING") {

            addAlert(
                container,
                "⚠️",
                `${bin.dustbin_id} odor warning`,
                "Elevated gas concentration detected.",
                "warning"
            );

            alertCount++;

        }

    });


    if (alertCount === 0) {

        container.innerHTML = `
            <div class="alert success">
                <span class="alert-icon">✓</span>
                <div>
                    <strong>All systems normal</strong>
                    <p>No critical waste alerts detected.</p>
                </div>
            </div>
        `;

    }

}


// ============================================
// CREATE ALERT
// ============================================

function addAlert(
    container,
    icon,
    title,
    message,
    type
) {

    const alert = document.createElement("div");

    alert.className = `alert ${type}`;

    alert.innerHTML = `
        <span class="alert-icon">${icon}</span>

        <div>
            <strong>${title}</strong>
            <p>${message}</p>
        </div>
    `;

    container.appendChild(alert);

}


// ============================================
// DUSTBIN TABLE
// ============================================

function updateDustbinTable() {

    const tableBody =
        document.querySelector("#dustbinTable tbody");

    if (!tableBody) return;


    tableBody.innerHTML = "";


    dustbins.forEach(bin => {

        const row = document.createElement("tr");


        const fill =
            Number(bin.fill_level || 0);


        const status =
            String(bin.status || "NORMAL").toUpperCase();


        row.innerHTML = `
            <td>
                <strong>${bin.dustbin_id}</strong>
            </td>

            <td>
                ${bin.location || "Unknown"}
            </td>

            <td>
                ${fill.toFixed(1)}%
            </td>

            <td>
                <span class="status-badge ${getStatusClass(status)}">
                    ${status}
                </span>
            </td>

            <td>
                ${formatNumber(bin.temperature)} °C
            </td>

            <td>
                ${formatNumber(bin.humidity)} %
            </td>

            <td>
                ${Math.round(Number(bin.gas_raw || 0))}
            </td>

            <td>
                ${bin.odor_status || "NORMAL"}
            </td>
        `;


        tableBody.appendChild(row);

    });

}


// ============================================
// STATUS CLASS
// ============================================

function getStatusClass(status) {

    switch (status) {

        case "FULL":
            return "status-full";

        case "NEAR_FULL":
            return "status-near-full";

        case "MEDIUM":
            return "status-medium";

        case "NORMAL":
            return "status-normal";

        default:
            return "status-normal";

    }

}


// ============================================
// CHART
// ============================================

function updateChart() {

    const canvas =
        document.getElementById("fillChart");

    if (!canvas) return;


    const labels =
        dustbins.map(bin => bin.dustbin_id);


    const values =
        dustbins.map(bin =>
            Number(bin.fill_level || 0)
        );


    if (typeof Chart === "undefined") {

        console.warn("Chart.js not loaded");

        return;

    }


    if (fillChart) {

        fillChart.data.labels = labels;

        fillChart.data.datasets[0].data = values;

        fillChart.update();

        return;

    }


    fillChart = new Chart(canvas, {

        type: "bar",

        data: {

            labels: labels,

            datasets: [

                {
                    label: "Fill Level (%)",

                    data: values,

                    borderWidth: 1
                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            scales: {

                y: {

                    beginAtZero: true,

                    max: 100,

                    title: {

                        display: true,

                        text: "Fill Level (%)"

                    }

                }

            },

            plugins: {

                legend: {

                    display: true

                }

            }

        }

    });

}


// ============================================
// HELPER
// ============================================

function updateElement(id, value) {

    const element =
        document.getElementById(id);

    if (element) {

        element.textContent = value;

    }

}


function formatNumber(value) {

    const number = Number(value);

    if (isNaN(number)) {

        return "0.0";

    }

    return number.toFixed(1);

}


// ============================================
// SUMMARY FALLBACK
// ============================================

function updateSummary(
    total,
    full,
    medium,
    empty
) {

    updateElement("totalBins", total);

    updateElement("fullBins", full);

    updateElement("mediumBins", medium);

    updateElement("emptyBins", empty);

}


// ============================================
// SYSTEM ERROR
// ============================================

function showSystemError() {

    const container =
        document.getElementById("alertsContainer");

    if (!container) return;


    container.innerHTML = `
        <div class="alert danger">

            <span class="alert-icon">❌</span>

            <div>

                <strong>System connection error</strong>

                <p>
                    Unable to retrieve latest dustbin data.
                    Please check the Flask server.
                </p>

            </div>

        </div>
    `;

}