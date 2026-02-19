import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os


def generate_data():
    """Generate 30 days of synthetic bus trip data."""
    
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

                    # Peak hours have more delay
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
    return df


def analyze_data(df):
    """Perform delay analysis."""
    
    df['delay'] = (df['actual'] - df['scheduled']).dt.total_seconds() / 60
    df['hour'] = df['actual'].dt.hour

    print("\n" + "=" * 50)
    print("BUS DELAY ANALYSIS")
    print("=" * 50)

    print(f"\nTotal Records: {len(df):,}")
    print(f"Average Delay: {df['delay'].mean():.2f} minutes")
    print(f"Max Delay: {df['delay'].max():.2f} minutes")

    on_time = (df['delay'].abs() <= 2).mean() * 100
    print(f"On-Time Percentage: {on_time:.1f}%")

    print("\nWorst Routes:")
    print(df.groupby('route')['delay'].mean().sort_values(ascending=False))

    print("\nWorst Stops:")
    print(df.groupby('stop')['delay'].mean().sort_values(ascending=False))

    print("\nWorst Hours:")
    print(df.groupby('hour')['delay'].mean().sort_values(ascending=False).head(3))

    return df


def visualize_data(df):
    """Create and save visualization charts."""
    
    os.makedirs("output", exist_ok=True)

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
    plt.savefig("output/bus_analysis.png", dpi=150)
    plt.close()

    print("\nCharts saved inside 'output' folder.")


def save_data(df):
    """Save dataset to CSV file."""
    df.to_csv("output/bus_data.csv", index=False)
    print("Data saved as CSV.")


def main():
    df = generate_data()
    df = analyze_data(df)
    visualize_data(df)
    save_data(df)

    print("\nProject Completed Successfully!")


if __name__ == "__main__":
    main()
