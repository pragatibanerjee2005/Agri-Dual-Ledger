async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${url}`);
  }
  return response.json();
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
}

function renderFraudTable(rows) {
  const body = document.getElementById("fraudTableBody");
  if (!body) return;
  body.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.Year}</td>
      <td>${row.District}</td>
      <td>${row.Yield}</td>
      <td>${row.Predicted_Yield}</td>
      <td>${row.FraudScore}</td>
    `;
    body.appendChild(tr);
  });
}

function renderLedgerTable(rows) {
  const body = document.getElementById("ledgerTableBody");
  if (!body) return;
  body.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.block_id}</td>
      <td>${row.transaction_id}</td>
      <td>${row.district}</td>
      <td>${row.public_record.yield}</td>
      <td>${row.status}</td>
      <td>${row.block_hash}</td>
    `;
    body.appendChild(tr);
  });
}

function renderTrackingFeed(rows) {
  const body = document.getElementById("trackingTableBody");
  if (!body) return;
  body.innerHTML = "";
  rows.slice(0, 10).forEach((row) => {
    const statusClass = row.risk_level === "high" ? "status-high" : "status-low";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.transaction_id}</td>
      <td>${row.district}</td>
      <td>${row.actual_yield}</td>
      <td>${row.predicted_yield}</td>
      <td>${row.fraud_score}</td>
      <td class="${statusClass}">${row.risk_level.toUpperCase()}</td>
    `;
    body.appendChild(tr);
  });
}

function renderCharts(analytics) {
  const yearly = analytics.yearly;
  const yieldCanvas = document.getElementById("yieldChart");
  if (yieldCanvas) {
    new Chart(yieldCanvas, {
      type: "line",
      data: {
        labels: yearly.years,
        datasets: [
          {
            label: "Actual Yield",
            data: yearly.avg_yield,
            borderColor: "#36d889",
            backgroundColor: "rgba(54, 216, 137, 0.25)",
            fill: true,
            tension: 0.3,
          },
          {
            label: "AI Predicted Yield",
            data: yearly.avg_predicted_yield,
            borderColor: "#5bc0ff",
            backgroundColor: "rgba(91, 192, 255, 0.2)",
            fill: true,
            tension: 0.3,
          },
        ],
      },
      options: { responsive: true, plugins: { legend: { labels: { color: "#e8fff5" } } } },
    });
  }

  const fraudCanvas = document.getElementById("fraudChart");
  if (fraudCanvas) {
    new Chart(fraudCanvas, {
      type: "bar",
      data: {
        labels: yearly.years,
        datasets: [
          {
            label: "Fraud Flags",
            data: yearly.fraud_counts,
            backgroundColor: "rgba(255, 109, 109, 0.8)",
            borderRadius: 8,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          x: { ticks: { color: "#a5c7ba" } },
          y: { ticks: { color: "#a5c7ba" } },
        },
        plugins: { legend: { labels: { color: "#e8fff5" } } },
      },
    });
  }
}

async function hydratePage() {
  try {
    const [overview, analytics, fraud, ledger, tracking] = await Promise.all([
      getJson("/api/overview"),
      getJson("/api/analytics"),
      getJson("/api/fraud"),
      getJson("/api/ledger"),
      getJson("/api/tracking"),
    ]);

    setText("totalRecords", overview.total_records);
    setText("fraudCases", overview.fraud_cases);
    setText("averageYield", overview.average_yield);
    setText("verifiedCases", overview.verified_cases);
    setText("fraudRate", `${overview.fraud_rate}%`);

    renderFraudTable(fraud.cases || []);
    renderLedgerTable(ledger.ledger_records || []);
    renderTrackingFeed(tracking.supply_chain_feed || []);
    renderCharts(analytics);
  } catch (error) {
    setText("pageStatus", "Could not load some live data.");
    // eslint-disable-next-line no-console
    console.error(error);
  }
}

hydratePage();
