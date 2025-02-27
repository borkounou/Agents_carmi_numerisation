// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';


// fetch("/admin/categories-birth-data")
//     .then(response => response.json())
//     .then(data => {
//         const labels = Object.keys(data.data); // Categories
//         const birthYears = new Set(); // Collect unique birth years
//         const datasets = [];

//         // Prepare datasets
//         Object.entries(data.data).forEach(([category, birthYearData]) => {
//             Object.keys(birthYearData).forEach(birthYear => {
//                 birthYears.add(birthYear);
//             });
//         });

//         // Sort birth years in ascending order
//         const sortedBirthYears = Array.from(birthYears).sort((a, b) => a - b);

//         sortedBirthYears.forEach(birthYear => {
//             datasets.push({
//                 label: birthYear, // Use birth year as the label
//                 data: labels.map(label => data.data[label][birthYear] || 0), // Fill missing data with 0
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
//                     display: false // Hide the legend
//                 },
//                 scales: {
//                     y: {
//                         beginAtZero: true
//                     }
//                 }
//             }
//         });
//     });


// function getRandomColor() {
//     const letters = '0123456789ABCDEF';
//     let color = '#';
//     for (let i = 0; i < 6; i++) {
//         color += letters[Math.floor(Math.random() * 16)];
//     }
//     return color;
// }




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

        // Aggregate data for the pie chart
        const aggregatedData = labels.map(label => {
            return sortedBirthYears.reduce((total, birthYear) => {
                return total + (data.data[label][birthYear] || 0);
            }, 0);
        });

        // Generate pie chart
        const ctx = document.getElementById("myAreaChart").getContext("2d");
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels, // Categories
                datasets: [{
                    data: aggregatedData, // Aggregated data for each category
                    backgroundColor: labels.map(() => getRandomColor()), // Assign random colors
                }],
            },
            options: {
                legend: {
                    display: false // Hide the legend
                }
            }
        });
    });

// Helper function to generate random colors
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}