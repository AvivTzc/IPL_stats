from flask import Flask, jsonify
import requests
import pandas as pd

app = Flask(__name__)

# כתובות ה-API
STATS_API_URL = "https://cdnapi.bamboo-video.com/api/football/stats?format=json&iid=573881b7181f46ae4c8b4567&filter={%22tournamentId%22:902,%22seasonName%22:%2224/25%22,%22round%22:0}&returnZeros=false&expand=[%22playerInstatId%22,%22teamInstatId%22]&disableDefaultFilter=true"
PLAYERS_API_URL = "https://cdnapi.bamboo-video.com/api/football/player?format=json&iid=573881b7181f46ae4c8b4567&returnZeros=false&expand=[%22instatId%22,%22teamInstatId%22]&disableDefaultFilter=true&useCache=false&ts=28962619"

@app.route('/', methods=['GET'])
def home():
    return "The server is running! Go to /combined-data to see the integrated stats with player names."

@app.route('/combined-data', methods=['GET'])
def get_combined_data():
    try:
        # שליפת הנתונים מה-API
        stats_response = requests.get(STATS_API_URL)
        players_response = requests.get(PLAYERS_API_URL)

        if stats_response.status_code == 200 and players_response.status_code == 200:
            # המרת התגובות ל-JSON
            stats_data = stats_response.json()
            players_data = players_response.json()

            if "data" in stats_data and "data" in players_data:
                # יצירת DataFrame מהנתונים
                stats_df = pd.DataFrame(stats_data["data"].values())
                players_df = pd.DataFrame(players_data["data"].values())

                # התאמת שם השחקן לפי `instatId`
                combined_df = stats_df.merge(
                    players_df[["instatId", "firstName", "lastName"]], 
                    how="left", 
                    left_on="instatId", 
                    right_on="instatId"
                )

                # הוספת עמודת "fullName" משם פרטי ושם משפחה
                combined_df["fullName"] = combined_df["firstName"] + " " + combined_df["lastName"]

                # החזרת הנתונים כ-JSON שטוח
                return jsonify(combined_df.to_dict(orient="records"))
            else:
                return jsonify({"error": "Data not found in one of the APIs"}), 404
        else:
            return jsonify({"error": f"Failed to fetch data from APIs. Stats: {stats_response.status_code}, Players: {players_response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
