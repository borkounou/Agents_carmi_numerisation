// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';


// Define the chart instance
var ctx = document.getElementById("myBarChart");
var myBarChart;

// Function to fetch data and update the chart
async function fetchChartData() {
  try {
    // Fetch data from the backend
    const response = await fetch("/admin/categories-data");
    const responseData = await response.json();
    
    // Extract labels and data
    const labels = responseData.data.map(item => item.category);
    const data = responseData.data.map(item => item.count);

    // Update the chart
    if (myBarChart) {
      myBarChart.destroy(); // Destroy the previous chart instance
    }

    myBarChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: "Count",
          backgroundColor: labels.map(() => getRandomColor()), 
          borderColor: "rgba(2,117,216,1)",
          data: data,
        }],
      },
      options: {
        legend: {
          display: false
        },
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true,
            },
          }],
        },
      },
    });
  } catch (error) {
    console.error("Error fetching chart data:", error);
  }
}

// Call the function on page load
fetchChartData();


function getRandomColor() {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}


