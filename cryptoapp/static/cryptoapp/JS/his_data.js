// Assuming exchangeRatesData is an array of objects with 'date' and 'rate' properties
// const labels = exchangeRatesData.map(data => data.fields.date);
// const rates = exchangeRatesData.map(data => parseFloat(data.fields.rate));

const lastData = exchangeRatesData.slice(-40);

// 用这30个元素创建labels和rates
const labels = lastData.map(data => data.fields.date);
const rates = lastData.map(data => parseFloat(data.fields.rate));

const data = {
    labels: labels,
    datasets: [{
        // label: 'Exchange Rate',
        backgroundColor: 'rgb(0, 128, 0)',
        borderColor: 'rgb(0, 128, 0)',
        borderWidth: 2,
        pointRadius: 0,
        data: rates,
    }]
};

const config = {
    type: 'line',
    data: data,
    options: {
        plugins: {
            legend: {
                display: false
            }
        }
    }

};

const exchangeRateChart = new Chart(
    document.getElementById('exchangeRateChart'),
    config
);
