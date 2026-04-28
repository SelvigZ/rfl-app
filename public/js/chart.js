(() => {
  const points = window.rflChartData || [];
  const canvas = document.getElementById("trendChart");
  const selectedDate = document.getElementById("selectedDate");
  const selectedWeight = document.getElementById("selectedWeight");
  const selectedWaist = document.getElementById("selectedWaist");

  if (!canvas || !points.length) {
    return;
  }

  const labels = points.map((point) => {
    const date = new Date(point.date + "T00:00:00");
    return date.toLocaleDateString("en-US", { month: "short", day: "2-digit" }).replace(" ", "-");
  });

  const updateSelectedPanel = (index) => {
    const point = points[index];
    if (!point) {
      return;
    }
    selectedDate.textContent = point.date;
    selectedWeight.textContent = `${Number(point.weight).toFixed(2)} lbs`;
    selectedWaist.textContent = `${Number(point.waist).toFixed(2)} in`;
  };

  const selectedPointPlugin = {
    id: "selectedPointPlugin",
    afterEvent(chart, args) {
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
      chart.$selectedIndex = pointIndex;
      updateSelectedPanel(pointIndex);
      chart.draw();
    },
    afterDatasetsDraw(chart) {
      if (chart.$selectedIndex == null) {
        return;
      }
      const meta = chart.getDatasetMeta(0);
      const element = meta.data[chart.$selectedIndex];
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
  };

  const chart = new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Weight (lbs)",
          data: points.map((point) => point.weight),
          borderColor: "#7ee6ff",
          backgroundColor: "rgba(126, 230, 255, 0.18)",
          pointBackgroundColor: "#7ee6ff",
          pointBorderColor: "#ffffff",
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBorderWidth: 2,
          tension: 0.25,
          yAxisID: "yWeight",
        },
        {
          label: "Waist (in)",
          data: points.map((point) => point.waist),
          borderColor: "#ff7a1a",
          backgroundColor: "rgba(255, 122, 26, 0.18)",
          pointBackgroundColor: "#ff7a1a",
          pointBorderColor: "#ffffff",
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBorderWidth: 2,
          tension: 0.25,
          yAxisID: "yWaist",
        },
      ],
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
          },
        },
        tooltip: {
          enabled: false,
        },
      },
      scales: {
        x: {
          ticks: {
            color: "#9ec8dc",
          },
          grid: {
            color: "rgba(158, 200, 220, 0.12)",
          },
        },
        yWeight: {
          type: "linear",
          position: "left",
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
          ticks: {
            color: "#ff9b3d",
          },
          grid: {
            drawOnChartArea: false,
          },
        },
      },
    },
    plugins: [selectedPointPlugin],
  });

  chart.$selectedIndex = points.length - 1;
  chart.draw();
})();
