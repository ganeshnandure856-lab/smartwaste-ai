// ============================================================
// SMART WASTE MANAGEMENT
// FRONTEND API CONNECTION
// ============================================================

// Your deployed Render backend
const API_URL = "https://smartwaste-ai-9mop.onrender.com/api/dustbin";

let fillChart = null;
let previousData = [];


// ============================================================
// FETCH DUSTBIN DATA
// ============================================================

async function fetchDustbins() {

    try {

        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("API request failed");
        }

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || "Unable to get data");
        }

        const dustbins = result.data || [];

        console.log("Dustbin data:", dustbins);

        updateDashboard(dustbins);

        previousData = dustbins;

    } catch (error) {

        console.error("API Error:", error);

        showConnectionError();

    }

}


// ============================================================
// UPDATE COMPLETE DASHBOARD
// ============================================================

function updateDashboard(dustbins) {

    updateSummary(dustbins);

    updateSensorCards(dustbins);

    updateDustbinTable(dustbins);

    updateAlerts(dustbins);

    updateChart(dustbins);

}


// ============================================================
// SUMMARY CARDS
// ============================================================

function updateSummary(dustbins) {

    const total = dustbins.length;

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


    document.getElementById("totalBins").textContent = total;

    document.getElementById("fullBins").textContent = full;

    document.getElementById("mediumBins").textContent = medium;

    document.getElementById("emptyBins").textContent = empty;

}


// ============================================================
// SENSOR CARDS
// ============================================================

function updateSensorCards(dustbins) {

    if (dustbins.length === 0) {

        document.getElementById("temperatureValue").textContent = "-- °C";

        document.getElementById("humidityValue").textContent = "-- %";

        document.getElementById("gasValue").textContent = "--";

        document.getElementById("odorValue").textContent = "--";

        document.getElementById("fillValue").textContent = "-- %";

        return;

    }


    // Use the first/current dustbin
    const bin = dustbins[0];


    // Temperature

    const temperature = Number(bin.temperature);

    document.getElementById("temperatureValue").textContent =
        isNaN(temperature)
            ? "-- °C"
            : `${temperature.toFixed(1)} °C`;


    // Humidity

    const humidity = Number(bin.humidity);

    document.getElementById("humidityValue").textContent =
        isNaN(humidity)
            ? "-- %"
            : `${humidity.toFixed(1)} %`;


    // Gas

    const gas = Number(bin.gas_raw);

    document.getElementById("gasValue").textContent =
        isNaN(gas)
            ? "--"
            : Math.round(gas);


    // Odor

    document.getElementById("odorValue").textContent =
        bin.odor_status || "--";


    // Fill Level

    const fill = Number(bin.fill_level);

    document.getElementById("fillValue").textContent =
        isNaN(fill)
            ? "-- %"
            : `${fill.toFixed(1)} %`;

}


// ============================================================
// DUSTBIN TABLE
// ============================================================

function updateDustbinTable(dustbins) {

    const table = document.getElementById("dustbinTable");


    if (!dustbins || dustbins.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="10">
                    No dustbin data available
                </td>
            </tr>
        `;

        return;

    }


    table.innerHTML = "";


    dustbins.forEach(bin => {

        const fill = Number(bin.fill_level || 0);

        const temperature = Number(bin.temperature);

        const humidity = Number(bin.humidity);

        const gas = Number(bin.gas_raw);

        const distance = Number(bin.distance);


        // Determine fill status

        let statusClass = "";
        let statusText = bin.status || "NORMAL";


        if (fill >= 70) {

            statusClass = "status-full";

            statusText = "FULL";

        } else if (fill >= 30) {

            statusClass = "status-medium";

            statusText = "MEDIUM";

        } else {

            statusClass = "status-empty";

            statusText = "EMPTY";

        }


        const row = document.createElement("tr");


        row.innerHTML = `

            <td>
                <strong>${escapeHTML(bin.dustbin_id || "--")}</strong>
            </td>

            <td>
                ${escapeHTML(bin.location || "--")}
            </td>

            <td>
                ${
                    isNaN(distance)
                        ? "--"
                        : distance.toFixed(1) + " cm"
                }
            </td>

            <td>

                <div class="fill-cell">

                    <div class="fill-bar">

                        <div
                            class="fill-progress"
                            style="width:${Math.min(fill, 100)}%"
                        ></div>

                    </div>

                    <span>
                        ${fill.toFixed(1)}%
                    </span>

                </div>

            </td>

            <td>
                ${
                    isNaN(temperature)
                        ? "--"
                        : temperature.toFixed(1) + " °C"
                }
            </td>

            <td>
                ${
                    isNaN(humidity)
                        ? "--"
                        : humidity.toFixed(1) + " %"
                }
            </td>

            <td>
                ${
                    isNaN(gas)
                        ? "--"
                        : Math.round(gas)
                }
            </td>

            <td>
                ${escapeHTML(bin.odor_status || "--")}
            </td>

            <td>

                <span class="status-badge ${statusClass}">
                    ${escapeHTML(statusText)}
                </span>

            </td>

            <td>
                ${formatDate(bin.timestamp || bin.updated_at)}
            </td>

        `;


        table.appendChild(row);

    });

}


// ============================================================
// ALERTS
// ============================================================

function updateAlerts(dustbins) {

    const container =
        document.getElementById("alertsContainer");


    const alerts = [];


    dustbins.forEach(bin => {

        const fill = Number(bin.fill_level || 0);

        const temperature = Number(bin.temperature);

        const odor =
            String(bin.odor_status || "").toUpperCase();


        // Fill alert

        if (fill >= 80) {

            alerts.push({

                type: "danger",

                message:
                    `${bin.dustbin_id} is critically full (${fill.toFixed(1)}%).`

            });

        } else if (fill >= 70) {

            alerts.push({

                type: "warning",

                message:
                    `${bin.dustbin_id} is almost full (${fill.toFixed(1)}%).`

            });

        }


        // Temperature alert

        if (!isNaN(temperature) && temperature >= 40) {

            alerts.push({

                type: "danger",

                message:
                    `${bin.dustbin_id} has high temperature (${temperature.toFixed(1)} °C).`

            });

        }


        // Odor alert

        if (
            odor === "BAD" ||
            odor === "HIGH" ||
            odor === "DETECTED"
        ) {

            alerts.push({

                type: "danger",

                message:
                    `${bin.dustbin_id} has an odor alert.`

            });

        }

    });


    if (alerts.length === 0) {

        container.innerHTML = `

            <div class="no-alert">

                ✅ No active alerts

            </div>

        `;

        return;

    }


    container.innerHTML = "";


    alerts.forEach(alert => {

        const div = document.createElement("div");

        div.className = `alert ${alert.type}`;


        div.innerHTML = `

            <span class="alert-icon">
                🚨
            </span>

            <span>
                ${escapeHTML(alert.message)}
            </span>

        `;


        container.appendChild(div);

    });

}


// ============================================================
// CHART
// ============================================================

function updateChart(dustbins) {

    if (!dustbins || dustbins.length === 0) {
        return;
    }


    const labels = [];

    const values = [];


    dustbins.forEach(bin => {

        labels.push(bin.dustbin_id || "Unknown");

        values.push(
            Number(bin.fill_level || 0)
        );

    });


    const canvas =
        document.getElementById("fillChart");


    if (!canvas) {
        return;
    }


    const ctx = canvas.getContext("2d");


    // Destroy previous chart

    if (fillChart) {

        fillChart.destroy();

    }


    fillChart = new Chart(ctx, {

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

                },

                x: {

                    title: {

                        display: true,

                        text: "Dustbin"

                    }

                }

            }

        }

    });

}


// ============================================================
// CONNECTION ERROR
// ============================================================

function showConnectionError() {

    const table =
        document.getElementById("dustbinTable");


    table.innerHTML = `

        <tr>

            <td colspan="10">

                ❌ Unable to connect to Smart Waste API

            </td>

        </tr>

    `;


    document.querySelector(".live-status").innerHTML = `

        <span class="live-dot"
              style="background:red">
        </span>

        OFFLINE

    `;

}


// ============================================================
// DATE FORMAT
// ============================================================

function formatDate(dateString) {

    if (!dateString) {
        return "--";
    }


    try {

        const date = new Date(dateString);

        return date.toLocaleString();

    } catch {

        return dateString;

    }

}


// ============================================================
// HTML SECURITY
// ============================================================

function escapeHTML(value) {

    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;

}


// ============================================================
// START DASHBOARD
// ============================================================

document.addEventListener("DOMContentLoaded", () => {

    console.log(
        "Smart Waste Dashboard started"
    );


    // First load

    fetchDustbins();


    // Refresh every 5 seconds

    setInterval(() => {

        fetchDustbins();

    }, 5000);

});