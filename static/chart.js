// chart.js
(function(){
  const DATA = window.__DATA__ || {};
  const forecast = DATA.forecast || [];

  // Helper function to insert the description line
  function addChartDescription(canvasElement, text) {
      const description = document.createElement('p');
      description.classList.add('chart-desc');
      description.textContent = text;
      // Insert the description right after the canvas
      canvasElement.insertAdjacentElement('afterend', description);
  }

  // Prepare arrays
  const labels = forecast.map(d => d.date);
  const temps = forecast.map(d => d.temp);
  const hums = forecast.map(d => d.humidity);
  const conds = forecast.map(d => d.description);

  // --- 1. Temperature Line Chart ---
  const tCtx = document.getElementById('tempChart').getContext('2d');
  new Chart(tCtx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Temp (°C)',
        data: temps,
        fill: true,
        tension: 0.3,
        borderColor: '#3fe7c9',
        backgroundColor: 'rgba(63,231,201,0.08)',
        pointRadius: 3
      }]
    },
    options: {
      responsive:true,
      plugins:{legend:{display:false}},
      scales:{ y:{ beginAtZero:false } }
    }
  });

  // Add description for Temperature Chart
  addChartDescription(tCtx.canvas, 'This line chart shows the daily high temperature trend over the forecast period.');


  // --- 2. Humidity Bar Chart ---
  const hCtx = document.getElementById('humChart').getContext('2d');
  new Chart(hCtx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label:'Humidity %',
        data: hums,
        backgroundColor: 'rgba(63,231,201,0.12)',
        borderColor: '#3fe7c9',
        borderWidth:1
      }]
    },
    options:{ responsive:true, plugins:{legend:{display:false}} }
  });

  // Add description for Humidity Chart
  addChartDescription(hCtx.canvas, 'This bar chart illustrates the daily humidity percentage for the week.');


  // --- 3. Condition Pie Chart ---
  const condCount = {};
  conds.forEach(c => condCount[c] = (condCount[c] || 0) + 1);
  const pCtx = document.getElementById('condPie').getContext('2d');
  new Chart(pCtx, {
    type: 'pie',
    data: {
      labels: Object.keys(condCount),
      datasets: [{
        data: Object.values(condCount),
        // Using a more professional and distinct color set
        backgroundColor: [
            '#3fe7c9', // Aqua (Main Accent)
            '#a389f4', // Violet (Secondary Accent)
            '#f9c859', // Gold/Yellow
            '#ff8373', // Coral/Red
            '#73d8ff'  // Light Blue
        ]
      }]
    },
    options:{
      responsive:true,
      maintainAspectRatio: false
    }
  });

  // Add description for Condition Pie Chart
  addChartDescription(pCtx.canvas, 'This pie chart displays primary weather conditions across the forecast.');

})();