(() => {
  const chartGroups = window.rflCharts || { dashboard: window.rflChartData || [] };
  const canvases = document.querySelectorAll("[data-rfl-chart]");

  if (!canvases.length || typeof Chart === "undefined") {
    return;
  }

  const toNumber = (value) => {
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  };

  const parseLocalDate = (dateText) => {
    const [year, month, day] = String(dateText).split("-").map(Number);
    if (!year || !month || !day) {
      return null;
    }
    return new Date(year, month - 1, day);
  };

  const formatShortDate = (dateText) => {
    const date = parseLocalDate(dateText);
    if (!date) {
      return dateText;
    }
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" }).replace(" ", "-");
  };

  const formatFullDate = (dateText) => {
    const date = parseLocalDate(dateText);
    if (!date) {
      return dateText || "No data";
    }

    const month = date.toLocaleDateString("en-US", { month: "short" });
    const day = String(date.getDate()).padStart(2, "0");
    return `${month}-${day}-${date.getFullYear()}`;
  };

  const formatValue = (value, unit) => {
    const number = toNumber(value);
    return number == null ? "No data" : `${number.toFixed(2)} ${unit}`;
  };

  const rollingAverage = (points, field, windowSize = 7) => {
    return points.map((point, index) => {
      const windowStart = Math.max(0, index - windowSize + 1);
      const values = points
        .slice(windowStart, index + 1)
        .map((row) => toNumber(row[field]))
        .filter((value) => value != null);

      if (!values.length || toNumber(point[field]) == null) {
        return null;
      }

      return values.reduce((sum, value) => sum + value, 0) / values.length;
    });
  };

  const axisBounds = (datasets, fallbackMin, fallbackMax) => {
    const values = datasets
      .flat()
      .map(toNumber)
      .filter((value) => value != null);

    if (!values.length) {
      return { min: fallbackMin, max: fallbackMax };
    }

    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = Math.max(max - min, 0.1);
    const padding = Math.max(range * 0.18, range < 1 ? 0.25 : 0.75);

    return {
      min: Number((min - padding).toFixed(2)),
      max: Number((max + padding).toFixed(2)),
    };
  };

  const separatedAxisBounds = (weightDatasets, waistDatasets) => {
    const weightBounds = axisBounds(weightDatasets, 150, 250);
    const waistBounds = axisBounds(waistDatasets, 25, 45);
    const weightRange = weightBounds.max - weightBounds.min;
    const waistRange = waistBounds.max - waistBounds.min;

    return {
      weight: {
        min: Number((weightBounds.min - weightRange * 0.08).toFixed(2)),
        max: Number((weightBounds.max + weightRange * 0.22).toFixed(2)),
      },
      waist: {
        min: Number((waistBounds.min - waistRange * 0.22).toFixed(2)),
        max: Number((waistBounds.max + waistRange * 0.08).toFixed(2)),
      },
    };
  };

  const makeSelectedPointPlugin = (points, selectedTargets) => ({
    id: `selectedPointPlugin-${selectedTargets.prefix}`,
    afterEvent(chart, args) {
      if (!selectedTargets.date || !selectedTargets.weight || !selectedTargets.waist) {
        return;
      }

      const event = args.event;
      if (!event || (event.type !== "click" && event.type !== "mouseup" && event.type !== "touchend")) {
        return;
      }

      const hitPoints = chart.getElementsAtEventForMode(
        event,
        "nearest",
        { intersect: false },
        true
      );

      if (!hitPoints.length) {
        return;
      }

      const pointIndex = hitPoints[0].index;
      const point = points[pointIndex];
      if (!point) {
        return;
      }

      chart.$selectedIndex = pointIndex;
      selectedTargets.date.textContent = formatFullDate(point.date);
      selectedTargets.weight.textContent = formatValue(point.weight, "lbs");
      selectedTargets.waist.textContent = formatValue(point.waist, "in");
      chart.draw();
    },
    afterDatasetsDraw(chart) {
      if (chart.$selectedIndex == null) {
        return;
      }

      const visibleMeta = chart.data.datasets
        .map((_, index) => chart.getDatasetMeta(index))
        .find((meta) => meta.data[chart.$selectedIndex]);
      const element = visibleMeta?.data[chart.$selectedIndex];
      if (!element) {
        return;
      }

      const { ctx, chartArea } = chart;
      ctx.save();
      ctx.strokeStyle = "rgba(255, 155, 61, 0.7)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(element.x, chartArea.top);
      ctx.lineTo(element.x, chartArea.bottom);
      ctx.stroke();
      ctx.restore();
    },
  });

  const renderChart = (canvas, points) => {
    if (!points.length) {
      return;
    }

    const showTrendlines = canvas.dataset.rflTrendlines !== "false";
    const labels = points.map((point) => formatShortDate(point.date));
    const weightValues = points.map((point) => toNumber(point.weight));
    const waistValues = points.map((point) => toNumber(point.waist));
    const weightTrend = showTrendlines ? rollingAverage(points, "weight") : [];
    const waistTrend = showTrendlines ? rollingAverage(points, "waist") : [];
    const bounds = separatedAxisBounds([weightValues, weightTrend], [waistValues, waistTrend]);
    const selectedTargets = {
      prefix: canvas.id || canvas.dataset.rflChart,
      date: document.getElementById(canvas.dataset.selectedDate || "selectedDate"),
      weight: document.getElementById(canvas.dataset.selectedWeight || "selectedWeight"),
      waist: document.getElementById(canvas.dataset.selectedWaist || "selectedWaist"),
    };

    const datasets = [
      {
        label: "Weight (lbs)",
        data: weightValues,
        borderColor: "#7ee6ff",
        backgroundColor: "rgba(126, 230, 255, 0.18)",
        pointBackgroundColor: "#7ee6ff",
        pointBorderColor: "#ffffff",
        pointRadius: 4,
        pointHoverRadius: 7,
        pointBorderWidth: 2,
        tension: 0.25,
        spanGaps: true,
        yAxisID: "yWeight",
      },
      {
        label: "Waist (in)",
        data: waistValues,
        borderColor: "#ff7a1a",
        backgroundColor: "rgba(255, 122, 26, 0.18)",
        pointBackgroundColor: "#ff7a1a",
        pointBorderColor: "#ffffff",
        pointRadius: 4,
        pointHoverRadius: 7,
        pointBorderWidth: 2,
        tension: 0.25,
        spanGaps: true,
        yAxisID: "yWaist",
      },
    ];

    if (showTrendlines) {
      datasets.push(
        {
          label: "Weight 7-day avg",
          data: weightTrend,
          borderColor: "rgba(126, 230, 255, 0.72)",
          borderDash: [7, 5],
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.28,
          spanGaps: true,
          yAxisID: "yWeight",
        },
        {
          label: "Waist 7-day avg",
          data: waistTrend,
          borderColor: "rgba(255, 155, 61, 0.78)",
          borderDash: [7, 5],
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.28,
          spanGaps: true,
          yAxisID: "yWaist",
        }
      );
    }

    const chart = new Chart(canvas, {
      type: "line",
      data: {
        labels,
        datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "nearest",
          intersect: false,
        },
        plugins: {
          legend: {
            labels: {
              color: "#d9eef8",
              usePointStyle: true,
            },
          },
          tooltip: {
            callbacks: {
              label(context) {
                const unit = context.dataset.yAxisID === "yWeight" ? "lbs" : "in";
                return `${context.dataset.label}: ${formatValue(context.parsed.y, unit)}`;
              },
            },
          },
        },
        scales: {
          x: {
            ticks: {
              color: "#9ec8dc",
              maxRotation: 0,
              autoSkip: true,
            },
            grid: {
              color: "rgba(158, 200, 220, 0.12)",
            },
          },
          yWeight: {
            type: "linear",
            position: "left",
            min: bounds.weight.min,
            max: bounds.weight.max,
            title: {
              display: true,
              text: "Weight (lbs)",
              color: "#7ee6ff",
            },
            ticks: {
              color: "#7ee6ff",
            },
            grid: {
              color: "rgba(158, 200, 220, 0.12)",
            },
          },
          yWaist: {
            type: "linear",
            position: "right",
            min: bounds.waist.min,
            max: bounds.waist.max,
            title: {
              display: true,
              text: "Waist (in)",
              color: "#ff9b3d",
            },
            ticks: {
              color: "#ff9b3d",
            },
            grid: {
              drawOnChartArea: false,
            },
          },
        },
      },
      plugins: [makeSelectedPointPlugin(points, selectedTargets)],
    });

    chart.$selectedIndex = points.length - 1;
    chart.draw();
  };

  canvases.forEach((canvas) => {
    const key = canvas.dataset.rflChart;
    const points = chartGroups[key] || [];
    renderChart(canvas, points);
  });
})();
