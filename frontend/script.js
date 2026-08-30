// ============================================================
// SMART WASTE MANAGEMENT
// DASHBOARD JAVASCRIPT
// ============================================================


const API_URL = "/api/dustbin";

let fillChart = null;


// ============================================================
// FETCH DATA
// ============================================================

async function fetchDustbinData() {

    try {

        const response =
            await fetch(API_URL);


        if (!response.ok) {

            throw new Error(
                "Server returned " +
                response.status
            );

        }


        const result =
            await response.json();


        if (!result.success) {

            throw new Error(
                "API returned unsuccessful response"
            );

        }


        updateDashboard(
            result.data
        );


        updateChart(
            result.data
        );

    }

    catch (error) {

        console.error(
            "Error fetching dustbin data:",
            error
        );

    }

}


// ============================================================
// UPDATE DASHBOARD
// ============================================================

function updateDashboard(readings) {

    if (
        !readings ||
        readings.length === 0
    ) {

        document.getElementById(
            "dustbinTable"
        ).innerHTML = `

            <tr>

                <td colspan="10">

                    No dustbin data available.

                </td>

            </tr>

        `;


        updateSummary([]);

        updateAlerts([]);

        return;

    }


    // --------------------------------------------------------
    // FIND LATEST READING
    // FOR EACH DUSTBIN
    // --------------------------------------------------------

    const latestBins = {};


    readings.forEach(
        reading => {

            const id =
                reading.dustbin_id;


            if (
                !latestBins[id] ||
                new Date(
                    reading.timestamp
                ) >
                new Date(
                    latestBins[id].timestamp
                )
            ) {

                latestBins[id] =
                    reading;

            }

        }
    );


    const bins =
        Object.values(
            latestBins
        );


    updateSummary(
        bins
    );


    updateTable(
        bins
    );


    updateSensorCards(
        bins
    );


    updateAlerts(
        bins
    );

}


// ============================================================
// SENSOR CARDS
// ============================================================

function updateSensorCards(bins) {

    if (
        !bins ||
        bins.length === 0
    ) {

        return;

    }


    const bin =
        bins[0];


    // Temperature

    document.getElementById(
        "temperatureValue"
    ).textContent =

        bin.temperature !== null &&
        bin.temperature !== undefined

        ? Number(
            bin.temperature
          ).toFixed(1) +
          " °C"

        : "-- °C";


    // Humidity

    document.getElementById(
        "humidityValue"
    ).textContent =

        bin.humidity !== null &&
        bin.humidity !== undefined

        ? Number(
            bin.humidity
          ).toFixed(1) +
          " %"

        : "-- %";


    // Gas

    document.getElementById(
        "gasValue"
    ).textContent =

        bin.gas_raw !== null &&
        bin.gas_raw !== undefined

        ? bin.gas_raw

        : "--";


    // Odor

    document.getElementById(
        "odorValue"
    ).textContent =

        bin.odor_status ||
        "--";


    // Fill

    document.getElementById(
        "fillValue"
    ).textContent =

        bin.fill_level !== null &&
        bin.fill_level !== undefined

        ? Number(
            bin.fill_level
          ).toFixed(1) +
          " %"

        : "-- %";

}


// ============================================================
// SUMMARY
// ============================================================

function updateSummary(bins) {

    let full = 0;

    let medium = 0;

    let empty = 0;


    bins.forEach(
        bin => {

            const status =
                String(
                    bin.status
                ).toUpperCase();


            if (
                status === "FULL"
            ) {

                full++;

            }

            else if (
                status === "MEDIUM"
            ) {

                medium++;

            }

            else {

                empty++;

            }

        }
    );


    document.getElementById(
        "totalBins"
    ).textContent =
        bins.length;


    document.getElementById(
        "fullBins"
    ).textContent =
        full;


    document.getElementById(
        "mediumBins"
    ).textContent =
        medium;


    document.getElementById(
        "emptyBins"
    ).textContent =
        empty;

}


// ============================================================
// ALERT SYSTEM
// ============================================================

function updateAlerts(bins) {

    const container =
        document.getElementById(
            "alertsContainer"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    let alertCount = 0;


    bins.forEach(
        bin => {

            const fillLevel =
                Number(
                    bin.fill_level || 0
                );


            const odor =
                String(
                    bin.odor_status ||
                    "NORMAL"
                ).toUpperCase();


            const binID =
                escapeHTML(
                    bin.dustbin_id
                );


            // ------------------------------------------------
            // FULL BIN
            // ------------------------------------------------

            if (
                fillLevel >= 80
            ) {

                const alert =
                    document.createElement(
                        "div"
                    );


                alert.className =
                    "alert alert-full";


                alert.innerHTML = `

                    <div class="alert-icon">
                        🗑️
                    </div>

                    <div>

                        <strong>
                            COLLECTION REQUIRED
                        </strong>

                        <p>
                            ${binID}
                            is
                            ${fillLevel.toFixed(1)}%
                            full.
                        </p>

                    </div>

                `;


                container.appendChild(
                    alert
                );


                alertCount++;

            }


            // ------------------------------------------------
            // HIGH ODOR
            // ------------------------------------------------

            if (
                odor === "HIGH"
            ) {

                const alert =
                    document.createElement(
                        "div"
                    );


                alert.className =
                    "alert alert-odor";


                alert.innerHTML = `

                    <div class="alert-icon">
                        👃
                    </div>

                    <div>

                        <strong>
                            HIGH ODOR ALERT
                        </strong>

                        <p>
                            ${binID}
                            has detected
                            high gas/odor level.
                        </p>

                    </div>

                `;


                container.appendChild(
                    alert
                );


                alertCount++;

            }


            // ------------------------------------------------
            // MODERATE ODOR
            // ------------------------------------------------

            else if (
                odor === "MODERATE"
            ) {

                const alert =
                    document.createElement(
                        "div"
                    );


                alert.className =
                    "alert alert-moderate";


                alert.innerHTML = `

                    <div class="alert-icon">
                        ⚠️
                    </div>

                    <div>

                        <strong>
                            MODERATE ODOR
                        </strong>

                        <p>
                            ${binID}
                            has elevated
                            gas level.
                        </p>

                    </div>

                `;


                container.appendChild(
                    alert
                );


                alertCount++;

            }

        }
    );


    // --------------------------------------------------------
    // NO ALERT
    // --------------------------------------------------------

    if (
        alertCount === 0
    ) {

        container.innerHTML = `

            <div class="no-alert">

                ✅ No active alerts

            </div>

        `;

    }

}


// ============================================================
// TABLE
// ============================================================

function updateTable(bins) {

    const table =
        document.getElementById(
            "dustbinTable"
        );


    table.innerHTML = "";


    bins.forEach(
        bin => {

            const row =
                document.createElement(
                    "tr"
                );


            const status =
                String(
                    bin.status
                ).toUpperCase();


            let statusClass =
                "status-empty";


            if (
                status === "FULL"
            ) {

                statusClass =
                    "status-full";

            }

            else if (
                status === "MEDIUM"
            ) {

                statusClass =
                    "status-medium";

            }


            row.innerHTML = `

                <td>

                    <strong>

                        ${escapeHTML(
                            bin.dustbin_id
                        )}

                    </strong>

                </td>


                <td>

                    ${escapeHTML(
                        bin.location ||
                        "Unknown"
                    )}

                </td>


                <td>

                    ${Number(
                        bin.distance || 0
                    ).toFixed(1)}
                    cm

                </td>


                <td>

                    ${Number(
                        bin.fill_level || 0
                    ).toFixed(1)}
                    %

                </td>


                <td>

                    ${
                        bin.temperature !== null &&
                        bin.temperature !== undefined

                        ? Number(
                            bin.temperature
                          ).toFixed(1) +
                          " °C"

                        : "N/A"
                    }

                </td>


                <td>

                    ${
                        bin.humidity !== null &&
                        bin.humidity !== undefined

                        ? Number(
                            bin.humidity
                          ).toFixed(1) +
                          " %"

                        : "N/A"
                    }

                </td>


                <td>

                    ${
                        bin.gas_raw !== null &&
                        bin.gas_raw !== undefined

                        ? bin.gas_raw

                        : "N/A"
                    }

                </td>


                <td>

                    <span class="odor">

                        ${escapeHTML(
                            bin.odor_status ||
                            "N/A"
                        )}

                    </span>

                </td>


                <td>

                    <span
                        class="status ${statusClass}"
                    >

                        ${status}

                    </span>

                </td>


                <td>

                    ${formatDate(
                        bin.timestamp
                    )}

                </td>

            `;


            table.appendChild(
                row
            );

        }
    );

}


// ============================================================
// CHART
// ============================================================

function updateChart(readings) {

    const canvas =
        document.getElementById(
            "fillChart"
        );


    if (!canvas) {

        return;

    }


    const recentReadings =
        [...readings]
        .reverse()
        .slice(-30);


    if (
        recentReadings.length === 0
    ) {

        return;

    }


    const labels =
        recentReadings.map(
            reading =>

                formatChartTime(
                    reading.timestamp
                )
        );


    const values =
        recentReadings.map(
            reading =>

                Number(
                    reading.fill_level
                )
        );


    if (fillChart) {

        fillChart.destroy();

    }


    fillChart =
        new Chart(

            canvas,

            {

                type: "line",


                data: {

                    labels:
                        labels,


                    datasets: [

                        {

                            label:
                                "Fill Level (%)",


                            data:
                                values,


                            borderWidth: 3,


                            tension: 0.3,


                            fill: false,


                            pointRadius: 4

                        }

                    ]

                },


                options: {

                    responsive: true,


                    maintainAspectRatio:
                        false,


                    scales: {

                        y: {

                            min: 0,

                            max: 100,


                            title: {

                                display: true,

                                text:
                                    "Fill Level (%)"

                            }

                        },


                        x: {

                            title: {

                                display: true,

                                text:
                                    "Time"

                            }

                        }

                    }

                }

            }

        );

}


// ============================================================
// TIME
// ============================================================

function formatChartTime(
    timestamp
) {

    if (!timestamp) {

        return "";

    }


    const date =
        new Date(
            timestamp
        );


    if (
        isNaN(
            date.getTime()
        )
    ) {

        return timestamp;

    }


    return date.toLocaleTimeString();

}


// ============================================================
// DATE
// ============================================================

function formatDate(
    timestamp
) {

    if (!timestamp) {

        return "-";

    }


    const date =
        new Date(
            timestamp
        );


    if (
        isNaN(
            date.getTime()
        )
    ) {

        return timestamp;

    }


    return date.toLocaleString();

}


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHTML(value) {

    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}


// ============================================================
// INITIAL LOAD
// ============================================================

fetchDustbinData();


// ============================================================
// AUTO REFRESH
// ============================================================

setInterval(

    fetchDustbinData,

    5000

);