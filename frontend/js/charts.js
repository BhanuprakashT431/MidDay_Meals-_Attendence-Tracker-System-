/**
 * Lightweight Charting Utilities (Pure SVG & Canvas)
 * Zero external heavyweight dependencies for ultra-fast 2G/3G rendering.
 */

window.charts = {
  // Render Circular Progress Gauge for Attendance
  renderDonut(containerId, percentage, label) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const radius = 38;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;
    const color = percentage >= 85 ? "#2e7d32" : percentage >= 70 ? "#ff9800" : "#d32f2f";

    container.innerHTML = `
      <div class="donut-chart-wrapper">
        <svg viewBox="0 0 100 100" class="donut-svg">
          <circle cx="50" cy="50" r="${radius}" class="donut-bg" />
          <circle cx="50" cy="50" r="${radius}" class="donut-fill"
            stroke="${color}"
            stroke-dasharray="${circumference}"
            stroke-dashoffset="${offset}" />
        </svg>
        <div class="donut-text">
          <span class="donut-value">${percentage}%</span>
          <span class="donut-label">${label}</span>
        </div>
      </div>
    `;
  },

  // Render Horizontal Stock Bar
  renderStockBar(containerId, current, threshold, unit) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const maxScale = Math.max(threshold * 3, current * 1.2, 50);
    const pct = Math.min(100, Math.round((current / maxScale) * 100));
    const isLow = current <= threshold;
    const color = isLow ? "#d32f2f" : "#2e7d32";

    container.innerHTML = `
      <div class="stock-bar-track">
        <div class="stock-bar-fill" style="width: ${pct}%; background-color: ${color};"></div>
      </div>
      <div class="stock-bar-legend">
        <span>${current} ${unit}</span>
        <span class="${isLow ? 'text-danger' : 'text-muted'}">${isLow ? '⚠️ Low' : 'Adequate'}</span>
      </div>
    `;
  }
};
