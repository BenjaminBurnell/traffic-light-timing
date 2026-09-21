import csv
import time
import math
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# --- 1. Load your CSV ---
def load_signals():
    signals = []
    # Pointing directly to the path you provided
    filepath = r"C:\Users\benbu\OneDrive\Desktop\traffic-light-timing\templates\traffic-signals-timing.csv"
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # You MUST ensure your CSV has Lat/Lng data for this to map correctly.
                # Adjust the row.get("ColumnName") strings to match your exact CSV headers.
                signals.append({
                    "id": row.get("Signal_ID", "Unknown"),
                    "name": row.get("Intersection", "Unknown Location"),
                    "lat": float(row.get("Lat", 43.6532)), 
                    "lng": float(row.get("Lng", -79.3832)),
                    "cycle_length": int(row.get("Cycle_Length", 120))
                })
    except Exception as e:
        print(f"Error reading CSV: {e}")
        # Fallback dummy data for testing the map if the CSV fails to load
        signals = [
            {"id": "1", "name": "Yonge & Dundas", "lat": 43.6561, "lng": -79.3802, "cycle_length": 120},
            {"id": "2", "name": "Bay & Front", "lat": 43.6455, "lng": -79.3797, "cycle_length": 100}
        ]
    return signals

SIGNALS = load_signals()

# --- 2. Distance Math (Haversine Formula) ---
def get_distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000 # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/glosa')
def glosa_calc():
    user_lat = float(request.args.get('lat', 0))
    user_lng = float(request.args.get('lng', 0))
    user_speed_mps = float(request.args.get('speed', 0)) # Meters per second from browser

    # Find the closest signal
    closest_sig = None
    min_dist = float('inf')

    for sig in SIGNALS:
        dist = get_distance_meters(user_lat, user_lng, sig['lat'], sig['lng'])
        if dist < min_dist:
            min_dist = dist
            closest_sig = sig
            
    if not closest_sig:
        return jsonify({"error": "No signals found"}), 404

    # --- 3. Simulate Light State ---
    now_ms = int(time.time() * 1000)
    cycle_ms = closest_sig['cycle_length'] * 1000
    position_in_cycle = now_ms % cycle_ms
    
    # Simple simulation: 50% Green, 10% Yellow, 40% Red
    green_end = cycle_ms * 0.50
    yellow_end = green_end + (cycle_ms * 0.10)
    
    if position_in_cycle < green_end:
        state = "Green"
        time_left = (green_end - position_in_cycle) / 1000
    elif position_in_cycle < yellow_end:
        state = "Yellow"
        time_left = (yellow_end - position_in_cycle) / 1000
    else:
        state = "Red"
        time_left = (cycle_ms - position_in_cycle) / 1000

    # --- 4. GLOSA Speed Math ---
    optimal_speed_kmh = 0
    message = ""
    
    if state == "Red":
        # Calculate speed needed to arrive exactly when it turns Green
        speed_mps = min_dist / time_left if time_left > 0 else 0
        optimal_speed_kmh = speed_mps * 3.6
        if optimal_speed_kmh > 60:
            message = "Too far. Maintain normal speed."
        else:
            message = f"Drop speed to {int(optimal_speed_kmh)} km/h to hit Green."
    elif state == "Green":
        message = "Maintain speed, light is Green."
    else:
        message = "Prepare to stop."
        
    return jsonify({
        "intersection": closest_sig['name'],
        "distance_m": int(min_dist),
        "state": state,
        "time_left_sec": int(time_left),
        "advisory": message
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)