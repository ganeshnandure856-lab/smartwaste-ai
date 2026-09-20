// ============================================
// SMART WASTE MANAGEMENT DASHBOARD
// ============================================

let dustbins = [];
let selectedBinId = null;
let fillChart = null;


// ============================================
// PAGE INITIALIZATION
// ============================================

document.addEventListener("DOMContentLoaded", () => {

    console.log("Dashboard started");

    loadDustbins();

    setInterval(loadDustbins, 5000);

});


// ============================================
// LOAD DUSTBIN DATA
// ============================================

async function loadDustbins() {

    try {

        const response = await fetch("/api/dustbin");

        if (!response.ok) {
            throw new Error("Failed to load dustbins");
        }

        const result = await response.json();

        dustbins = Array.isArray(result)
            ? result
            : result.dustbins || result.data || [];

        console.log("Dustbins:", dustbins);

        updateDashboard();

    } catch (error) {

        console.error("Loading dustbins error:", error);

        showSystemError("Unable to load dustbin data");

    }

}


// ============================================
// UPDATE COMPLETE DASHBOARD
// ============================================

function updateDashboard() {

    if (dustbins.length === 0) {

        updateSummary(0, 0, 0, 0);

        return;

    }

    if (!selectedBinId) {

        selectedBinId = dustbins[0].dustbin_id;

    }

    const selectedExists = dustbins.some(
        bin => bin.dustbin_id === selectedBinId
    );

    if (!selectedExists) {

        selectedBinId = dustbins[0].dustbin_id;

    }

    updateSummaryCards();

    updateDustbinSelector();

    updateSensorCards();

    updateAIRisk();

    // AI FORECAST
    loadForecast(selectedBinId);

    updateAlerts();

    updateDustbinTable();

    updateChart();

}


// ============================================
// SUMMARY CARDS
// ============================================

function updateSummaryCards() {

    const totalBins = dustbins.length;

    let fullBins = 0;
    let mediumBins = 0;
    let emptyBins = 0;

    dustbins.forEach(bin => {

        const fillLevel = Number(bin.fill_level || 0);

        if (fillLevel >= 90) {

            fullBins++;

        } else if (fillLevel >= 30) {

            mediumBins++;

        } else {

            emptyBins++;

        }

    });

    updateSummary(
        totalBins,
        fullBins,
        mediumBins,
        emptyBins
    );

}


function updateSummary(total, full, medium, empty) {

    updateElement("totalBins", total);

    updateElement("fullBins", full);

    updateElement("mediumBins", medium);

    updateElement("emptyBins", empty);

}


// ============================================
// DUSTBIN SELECTOR
// ============================================

function updateDustbinSelector() {

    const selector = document.getElementById(
        "dustbinSelector"
    );

    if (!selector) return;

    selector.innerHTML = "";

    dustbins.forEach(bin => {

        const option = document.createElement("option");

        option.value = bin.dustbin_id;

        option.textContent =
            `${bin.dustbin_id} - ${
                bin.location || "Unknown Location"
            }`;

        if (bin.dustbin_id === selectedBinId) {

            option.selected = true;

        }

        selector.appendChild(option);

    });

    selector.onchange = function () {

        selectedBinId = this.value;

        updateDashboard();

    };

}


// ============================================
// SENSOR CARDS
// ============================================

function updateSensorCards() {

    const bin = dustbins.find(
        item => item.dustbin_id === selectedBinId
    );

    if (!bin) return;

    const fillLevel = Number(bin.fill_level || 0);

    const temperature = Number(bin.temperature || 0);

    const humidity = Number(bin.humidity || 0);

    const gasValue = Number(
        bin.gas_value ||
        bin.gas ||
        bin.mq_value ||
        bin.gas_raw ||
        0
    );

    updateElement(
        "fillValue",
        formatNumber(fillLevel) + "%"
    );

    updateElement(
        "temperatureValue",
        formatNumber(temperature) + "°C"
    );

    updateElement(
        "humidityValue",
        formatNumber(humidity) + "%"
    );

    updateElement(
        "gasValue",
        formatNumber(gasValue)
    );

    updateElement(
        "odorValue",
        getOdorStatus(gasValue)
    );

    console.log("Selected bin:", bin);

}


// ============================================
// ODOR STATUS
// ============================================

function getOdorStatus(gasValue) {

    if (gasValue >= 2500) {

        return "Danger";

    }

    if (gasValue >= 1500) {

        return "Warning";

    }

    return "Normal";

}


// ============================================
// LIVE AI OVERFLOW PREDICTION
// ============================================

async function updateAIRisk() {

    const bin = dustbins.find(
        item => item.dustbin_id === selectedBinId
    );

    if (!bin) return;

    try {

        updateElement(
            "aiModelStatus",
            "Analyzing..."
        );

        const response = await fetch(
            `/api/predict/${encodeURIComponent(
                selectedBinId
            )}`
        );

        if (!response.ok) {

            throw new Error(
                "Live prediction API failed"
            );

        }

        const result = await response.json();

        console.log("Live AI Prediction:", result);

        if (!result.success) {

            throw new Error(
                result.error || "Prediction failed"
            );

        }

        const percentage = Number(
            result.risk_percentage || 0
        );

        const riskStatus =
            result.overflow_risk === "YES"
                ? "🚨 Overflow Risk Detected"
                : "✅ Low Overflow Risk";

        updateElement(
            "aiRiskPercentage",
            percentage.toFixed(1) + "%"
        );

        updateElement(
            "aiRiskStatus",
            riskStatus
        );

        updateElement(
            "aiModelStatus",
            "Active"
        );

        updateElement(
            "aiLastUpdated",
            new Date().toLocaleTimeString()
        );

        console.log(
            `Bin: ${selectedBinId}, ` +
            `Fill: ${result.fill_level}%, ` +
            `Risk: ${percentage}%`
        );

    } catch (error) {

        console.error(
            "AI prediction error:",
            error
        );

        updateElement(
            "aiRiskStatus",
            "⚠️ Prediction unavailable"
        );

        updateElement(
            "aiRiskPercentage",
            "--%"
        );

        updateElement(
            "aiModelStatus",
            "Unavailable"
        );

        updateElement(
            "aiLastUpdated",
            "Error"
        );

    }

}


// ============================================
// AI WASTE FORECAST
// ============================================

async function loadForecast(dustbinId) {

    if (!dustbinId) return;

    try {

        const response = await fetch(
            `/api/forecast/${encodeURIComponent(dustbinId)}`
        );

        if (!response.ok) {

            throw new Error("Forecast API failed");

        }

        const data = await response.json();

        console.log("AI Forecast:", data);

        if (!data.success) {

            throw new Error(
                data.error || "Forecast unavailable"
            );

        }

        updateElement(
            "forecastCurrentFill",
            Number(data.current_fill).toFixed(2)
        );

        updateElement(
            "forecastFutureFill",
            Number(
                data.predicted_fill_after_2_hours
            ).toFixed(2)
        );

        updateElement(
            "forecastFillRate",
            Number(data.fill_rate_per_hour).toFixed(2)
        );

        const overflowTime =
            data.estimated_time_to_80_percent;

        if (overflowTime === null) {

            updateElement(
                "forecastTimeToOverflow",
                "Not currently estimated"
            );

        } else {

            updateElement(
                "forecastTimeToOverflow",
                overflowTime + " hours"
            );

        }

        let message = "";

        if (data.current_fill >= 80) {

            message =
                "🚨 Fill level is already above 80%. Collection recommended.";

        } else if (data.fill_rate_per_hour <= 0) {

            message =
                "ℹ️ No increasing fill trend detected.";

        } else {

            message =
                "✅ Forecast updated successfully.";

        }

        updateElement(
            "forecastMessage",
            message
        );

    } catch (error) {

        console.error(
            "Forecast error:",
            error
        );

        updateElement(
            "forecastCurrentFill",
            "--"
        );

        updateElement(
            "forecastFutureFill",
            "--"
        );

        updateElement(
            "forecastFillRate",
            "--"
        );

        updateElement(
            "forecastTimeToOverflow",
            "--"
        );

        updateElement(
            "forecastMessage",
            "⚠️ Forecast unavailable"
        );

    }

}


// ============================================
// ALERTS
// ============================================

function updateAlerts() {

    const container = document.getElementById(
        "alertsContainer"
    );

    if (!container) return;

    container.innerHTML = "";

    const bin = dustbins.find(
        item => item.dustbin_id === selectedBinId
    );

    if (!bin) {

        container.innerHTML =
            "<p>No dustbin selected.</p>";

        return;

    }

    const fillLevel = Number(bin.fill_level || 0);

    const gasValue = Number(
        bin.gas_value ||
        bin.gas ||
        bin.mq_value ||
        bin.gas_raw ||
        0
    );

    const alerts = [];

    if (fillLevel >= 90) {

        alerts.push(
            "🚨 Dustbin is full. Collection required."
        );

    } else if (fillLevel >= 70) {

        alerts.push(
            "⚠️ Dustbin is nearly full."
        );

    }

    if (gasValue >= 2500) {

        alerts.push(
            "🚨 High gas level detected."
        );

    } else if (gasValue >= 1500) {

        alerts.push(
            "⚠️ Gas level is increasing."
        );

    }

    if (alerts.length === 0) {

        container.innerHTML =
            "<p>✅ No active alerts.</p>";

        return;

    }

    alerts.forEach(alert => {

        const paragraph = document.createElement("p");

        paragraph.textContent = alert;

        container.appendChild(paragraph);

    });

}


// ============================================
// DUSTBIN TABLE
// ============================================

function updateDustbinTable() {

    const tableBody = document.getElementById(
        "dustbinTable"
    );

    if (!tableBody) return;

    tableBody.innerHTML = "";

    dustbins.forEach(bin => {

        const row = document.createElement("tr");

        const fillLevel = Number(bin.fill_level || 0);

        const status = getFillStatus(fillLevel);

        row.innerHTML = `

            <td>
                ${escapeHTML(bin.dustbin_id)}
            </td>

            <td>
                ${escapeHTML(
                    bin.location || "Unknown"
                )}
            </td>

            <td>
                ${fillLevel.toFixed(1)}%
            </td>

            <td>
                <span class="status-badge ${
                    status.className
                }">

                    ${status.label}

                </span>
            </td>

            <td>
                ${escapeHTML(
                    bin.timestamp || "N/A"
                )}
            </td>

        `;

        tableBody.appendChild(row);

    });

}


// ============================================
// FILL STATUS
// ============================================

function getFillStatus(fillLevel) {

    if (fillLevel >= 90) {

        return {
            label: "FULL",
            className: "status-full"
        };

    }

    if (fillLevel >= 30) {

        return {
            label: "MEDIUM",
            className: "status-medium"
        };

    }

    return {
        label: "EMPTY",
        className: "status-empty"
    };

}


// ============================================
// FILL LEVEL CHART
// ============================================

async function updateChart() {

    const canvas = document.getElementById(
        "fillChart"
    );

    if (!canvas || !selectedBinId) return;

    try {

        const response = await fetch(
            `/api/readings/${encodeURIComponent(
                selectedBinId
            )}`
        );

        if (!response.ok) {

            throw new Error(
                "Failed to load chart data"
            );

        }

        const result = await response.json();

        const readings = Array.isArray(result)
            ? result
            : result.readings ||
              result.data ||
              [];

        const labels = readings.map(
            reading =>
                formatTimestamp(reading.timestamp)
        );

        const values = readings.map(
            reading =>
                Number(reading.fill_level || 0)
        );

        if (fillChart) {

            fillChart.destroy();

        }

        fillChart = new Chart(
            canvas,
            {
                type: "line",

                data: {
                    labels: labels,

                    datasets: [
                        {
                            label: "Fill Level (%)",

                            data: values,

                            borderWidth: 2,

                            tension: 0.3,

                            fill: false
                        }
                    ]
                },

                options: {
                    responsive: true,

                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            }
        );

    } catch (error) {

        console.error(
            "Chart error:",
            error
        );

    }

}


// ============================================
// HELPER FUNCTIONS
// ============================================

function updateElement(id, value) {

    const element = document.getElementById(id);

    if (element) {

        element.textContent = value;

    }

}


function formatNumber(value) {

    const number = Number(value);

    if (isNaN(number)) {

        return "0";

    }

    return number.toFixed(1);

}


function formatTimestamp(timestamp) {

    if (!timestamp) {

        return "N/A";

    }

    try {

        const date = new Date(timestamp);

        if (isNaN(date.getTime())) {

            return timestamp;

        }

        return date.toLocaleTimeString();

    } catch (error) {

        return timestamp;

    }

}


function escapeHTML(value) {

    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;

}


function showSystemError(message) {

    console.error(message);

    const container = document.getElementById(
        "alertsContainer"
    );

    if (container) {

        container.innerHTML = `
            <p>
                ⚠️ ${escapeHTML(message)}
            </p>
        `;

    }

}