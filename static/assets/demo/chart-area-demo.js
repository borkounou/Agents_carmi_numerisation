// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Area Chart Example
var ctx = document.getElementById("myAreaChart");
datasets: 

var myLineChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels:  ["Agent Militaire", "Agent Militaire Veuve", "Agent Garde"],
    datasets: [{
      label: "Compensation",
      backgroundColor: ["rgba(2,117,216,1)", "rgba(92,184,92,1)", "rgba(240,173,78,1)"],
      borderColor: "rgba(2,117,216,1)",
      data: [120000, 80000, 50000],
  }],
  },
  options: {
    legend: {
      display: true
    }
  }
});
