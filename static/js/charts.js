function renderChart(data) {
    if (data.error) return;

    const ctx = document.getElementById('locationChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Latitude', 'Longitude'],
            datasets: [{
                label: 'Koordinatlar',
                data: [data.lat, data.lon],
                backgroundColor: ['#007bff', '#28a745'],
            }]
        }
    });
}