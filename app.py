from flask import Flask, jsonify
import requests
import pandas as pd

app = Flask(__name__)

# כתובת ה-API המקורי
API_URL = "https://cdnapi.bamboo-video.com/api/football/stats?format=json&iid=573881b7181f46ae4c8b4567&filter={%22tournamentId%22:902,%22seasonName%22:%2224/25%22,%22round%22:0}&returnZeros=false&expand=[%22playerInstatId%22,%22teamInstatId%22]&disableDefaultFilter=true"

@app.route('/flattened-data', methods=['GET'])
def get_flattened_data():
    # שליפת הנתונים מה-API המקורי
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        if "data" in data:
            # שיטוח הנתונים
            flat_data = []
            for key, value in data["data"].items():
                flat_data.append(value)
            
            # המרת הרשומות ל-DataFrame ואז ל-JSON פשוט
            df = pd.DataFrame(flat_data)
            return jsonify(df.to_dict(orient='records'))
        else:
            return jsonify({"error": "No data found in the response"}), 404
    else:
        return jsonify({"error": "Failed to fetch data from the API"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
