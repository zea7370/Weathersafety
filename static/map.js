// map.js
(function(){
  const DATA = window.__DATA__ || {};
  const w = DATA.weather || {};
  const key = DATA.openweather_key || '';

  const lat = w.lat || 0;
  const lon = w.lon || 0;
  const city = w.city || 'Location';

  // Initialize map
  const map = L.map('map').setView([lat, lon], 11);

  // Base tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
  }).addTo(map);

  // Marker
  L.marker([lat, lon]).addTo(map)
    .bindPopup(`<b>${city}</b><br>${w.temp}°C<br>${w.desc || ''}`).openPopup();

  // Optional OpenWeather overlay (temperature)
  if (key) {
    const layer = L.tileLayer(`https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${key}`, {
      opacity: 0.45,
      attribution: 'OpenWeather'
    });
    layer.addTo(map);
  }
})();
