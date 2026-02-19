import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from flask import Flask, jsonify, send_file

app = Flask(__name__)

OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def generate_data():
    np.random.seed(42)
    routes = ['R1', 'R2', 'R3']
    stops = ['Stop_A', 'Stop_B', 'Stop_C', 'Stop_D']
    data = []

    start_date = datetime.now() - timedelta(days=30)

    for day in range(30):
        date = start_date + timedelta(days=day)

        for route in routes:
            for trip in range(10):
                hour = 7 + trip

                for i, stop in enumerate(stops):
                    scheduled = date.replace(hour=hour, minute=i * 10, second=0)

                    if hour in [8, 9, 17]:
                        delay = np.random.normal(5, 2)
                    else:
                        delay = np.random.normal(1, 1)

                    actual = scheduled + timedelta(minutes=delay)

                    data.append({
                        'route': route,
                        'stop': stop,
                        'scheduled': scheduled,
                        'actual': actual
                    })

    df = pd.DataFrame(data)
    df['delay'] = (df['actual'] - df['scheduled']).dt.total_seconds() / 60
    df['hour'] = df['actual'].dt.hour

    return df


def analyze_data(df):
    summary = {
        "total_records": len(df),
        "average_delay": round(df['delay'].mean(), 2),
        "max_delay": round(df['delay'].max(), 2),
        "on_time_percentage": round((df['delay'].abs() <= 2).mean() * 100, 1),
        "worst_routes": df.groupby('route')['delay'].mean().sort_values(ascending=False).to_dict(),
        "worst_stops": df.groupby('stop')['delay'].mean().sort_values(ascending=False).to_dict(),
        "worst_hours": df.groupby('hour')['delay'].mean().sort_values(ascending=False).head(3).to_dict()
    }

    return summary


def create_visualization(df):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    axes[0, 0].hist(df['delay'], bins=30)
    axes[0, 0].set_title('Delay Distribution')

    hourly = df.groupby('hour')['delay'].mean()
    axes[0, 1].bar(hourly.index, hourly.values)
    axes[0, 1].set_title('Average Delay by Hour')

    route_delay = df.groupby('route')['delay'].mean()
    axes[1, 0].barh(route_delay.index, route_delay.values)
    axes[1, 0].set_title('Average Delay by Route')

    stop_delay = df.groupby('stop')['delay'].mean()
    axes[1, 1].bar(stop_delay.index, stop_delay.values)
    axes[1, 1].set_title('Average Delay by Stop')

    plt.tight_layout()
    filepath = os.path.join(OUTPUT_FOLDER, "bus_analysis.png")
    plt.savefig(filepath, dpi=150)
    plt.close()

    return filepath


@app.route("/")
def home():
    return "Bus Delay Analysis API is Running 🚍"


@app.route("/analyze")
def run_analysis():
    df = generate_data()
    summary = analyze_data(df)

    df.to_csv(os.path.join(OUTPUT_FOLDER, "bus_data.csv"), index=False)
    create_visualization(df)

    return jsonify(summary)


@app.route("/chart")
def get_chart():
    filepath = os.path.join(OUTPUT_FOLDER, "bus_analysis.png")
    return send_file(filepath, mimetype='image/png')


# IMPORTANT FOR GUNICORN
if __name__ == "__main__":
    app.run(debug=True)
