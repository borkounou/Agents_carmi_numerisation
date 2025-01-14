// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Bar Chart Example
var ctx = document.getElementById("myBarChart");

var myLineChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ["Agent Militaire", "Agent Militaire Veuve", "Agent Garde"],
    datasets: [{
      label: "Compensation",
      backgroundColor: ["rgba(2,117,216,1)", "rgba(92,184,92,1)", "rgba(240,173,78,1)"],
      borderColor: "rgba(2,117,216,1)",
      data: [120000, 80000, 60000],
    }],
  },
  options: {
    legend: {
      display: false
    },
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true, // Ensures the y-axis starts from 0
        },
      }],
    },
  },
});
