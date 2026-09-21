// DOM Elements
const statusText = document.getElementById('status-text');
const intersectionName = document.getElementById('intersection-name');
const timerDisplay = document.getElementById('countdown-timer');
const redLight = document.getElementById('light-red');
const yellowLight = document.getElementById('light-yellow');
const greenLight = document.getElementById('light-green');

// Mock Database of Intersections
const intersections = [
    {
        id: "simcoe_conlin",
        name: "Simcoe St & Conlin Rd",
        lat: 43.9448, 
        lon: -78.8962,
        cycleLength: 90,   
        greenDuration: 40, 
        yellowDuration: 5,
        syncOffset: 0      
    },
    {
        id: "founders_conlin",
        name: "Founders Dr & Conlin Rd",
        lat: 43.9465,
        lon: -78.8975,
        cycleLength: 60,
        greenDuration: 25,
        yellowDuration: 5,
        syncOffset: 0
    }
];

let activeIntersection = null;

// Haversine formula to calculate distance in meters
function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; 
    const p1 = lat1 * Math.PI/180;
    const p2 = lat2 * Math.PI/180;
    const dp = (lat2-lat1) * Math.PI/180;
    const dl = (lon2-lon1) * Math.PI/180;

    const a = Math.sin(dp/2) * Math.sin(dp/2) +
              Math.cos(p1) * Math.cos(p2) *
              Math.sin(dl/2) * Math.sin(dl/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c; 
}

// Start watching user location
if ("geolocation" in navigator) {
    navigator.geolocation.watchPosition((position) => {
        const userLat = position.coords.latitude;
        const userLon = position.coords.longitude;
        
        // Find closest intersection within 300 meters
        const approaching = intersections.find(intersection => {
            const distance = getDistance(userLat, userLon, intersection.lat, intersection.lon);
            return distance < 300; 
        });
        
        if (approaching) {
            activeIntersection = approaching;
            statusText.innerText = "Approaching";
            intersectionName.innerText = activeIntersection.name;
        } else {
            activeIntersection = null;
            resetUI();
        }
    }, (error) => {
        console.error("Geolocation error:", error);
        statusText.innerText = "Location Error";
        intersectionName.innerText = "Please enable location services";
    }, { enableHighAccuracy: true });
}

// Main Game/Timing Loop (Runs every 100ms for responsiveness, though seconds update once per sec)
setInterval(() => {
    if (!activeIntersection) return;

    const now = Math.floor(Date.now() / 1000); 
    const timeInCycle = (now + activeIntersection.syncOffset) % activeIntersection.cycleLength;
    
    let currentColor = "";
    let timeRemaining = 0;
    
    const redDuration = activeIntersection.cycleLength - (activeIntersection.greenDuration + activeIntersection.yellowDuration);

    // Calculate which phase the cycle is currently in
    if (timeInCycle < activeIntersection.greenDuration) {
        currentColor = "green";
        timeRemaining = activeIntersection.greenDuration - timeInCycle;
    } else if (timeInCycle < (activeIntersection.greenDuration + activeIntersection.yellowDuration)) {
        currentColor = "yellow";
        timeRemaining = (activeIntersection.greenDuration + activeIntersection.yellowDuration) - timeInCycle;
    } else {
        currentColor = "red";
        timeRemaining = activeIntersection.cycleLength - timeInCycle;
    }

    updateLights(currentColor);
    timerDisplay.innerText = timeRemaining;

}, 200);

function updateLights(color) {
    // Reset all
    redLight.classList.remove('active');
    yellowLight.classList.remove('active');
    greenLight.classList.remove('active');

    // Activate current
    if (color === "red") redLight.classList.add('active');
    if (color === "yellow") yellowLight.classList.add('active');
    if (color === "green") greenLight.classList.add('active');
}

function resetUI() {
    statusText.innerText = "Out of Range";
    intersectionName.innerText = "No supported intersections nearby";
    timerDisplay.innerText = "--";
    updateLights(""); // turns all off
}