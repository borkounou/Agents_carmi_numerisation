// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';


fetch("/admin/categories-birth-data")
    .then(response => response.json())
    .then(data => {
        const labels = Object.keys(data.data); // Categories
        const birthYears = new Set(); // Collect unique birth years
        const datasets = [];

        // Prepare datasets
        Object.entries(data.data).forEach(([category, birthYearData]) => {
            Object.keys(birthYearData).forEach(birthYear => {
                birthYears.add(birthYear);
            });
        });

        // Sort birth years in ascending order
        const sortedBirthYears = Array.from(birthYears).sort((a, b) => a - b);

        sortedBirthYears.forEach(birthYear => {
            datasets.push({
                label: birthYear, // Use birth year as the label
                data: labels.map(label => data.data[label][birthYear] || 0), // Fill missing data with 0
                borderColor: getRandomColor(),
                fill: false
            });
        });

        // Generate chart
        const ctx = document.getElementById("myAreaChart").getContext("2d");
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels, // Categories
                datasets: datasets
            },
            options: {
                legend: {
                    display: true
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    });


// fetch("/admin/categories-birth-data")
//     .then(response => response.json())
//     .then(data => {
//         const labels = Object.keys(data.data); // Categories
//         const birthPlaces = new Set(); // Collect unique birth places
//         const datasets = [];

//         // Prepare datasets
//         Object.entries(data.data).forEach(([category, birthPlaceData]) => {
//             Object.keys(birthPlaceData).forEach(birthPlace => {
//                 birthPlaces.add(birthPlace);
//             });
//         });

//         birthPlaces.forEach(birthPlace => {
//             datasets.push({
//                 label: birthPlace,
//                 data: labels.map(label => data.data[label][birthPlace] || 0), // Fill missing data with 0
//                 borderColor: getRandomColor(),
//                 fill: false
//             });
//         });

//         // Generate chart
//         const ctx = document.getElementById("myAreaChart").getContext("2d");
//         new Chart(ctx, {
//             type: 'line',
//             data: {
//                 labels: labels, // Categories
//                 datasets: datasets
//             },
//             options: {
//                 legend: {
//                     display: true
//                 },
//                 scales: {
//                     y: {
//                         beginAtZero: true
//                     }
//                 }
//             }
//         });
//     });

// // Helper function for random colors
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}


// // Area Chart Example
// var ctx = document.getElementById("myAreaChart");
// var myLineChart = new Chart(ctx, {
//   type: 'line',
//   data: {
//     labels:  ["Agent Militaire", "Agent Militaire Veuve", "Agent Garde"],
//     datasets: [{
//       label: "Compensation",
//       backgroundColor: ["rgba(2,117,216,1)", "rgba(92,184,92,1)", "rgba(240,173,78,1)"],
//       borderColor: "rgba(2,117,216,1)",
//       data: [120000, 80000, 50000],
//   }],
//   },
//   options: {
//     legend: {
//       display: true
//     }
//   }
// });
