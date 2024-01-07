import pandas as pd
import matplotlib.pyplot as plt

# Load and preprocess data
def load_and_preprocess_data(file_path):
    traffic_data = pd.read_csv(file_path)
    hourly_traffic_columns = [col for col in traffic_data.columns if '-' in col and traffic_data[col].dtype == 'float64']
    # Scale down traffic volumes (optional, based on dataset specifics)
    traffic_data[hourly_traffic_columns] = traffic_data[hourly_traffic_columns].apply(lambda x: x / max(x) * 100)
    return traffic_data, hourly_traffic_columns

# Fixed-Time Control Algorithm
def fixed_time_control(hour, peak_hours, high_duration_peak, low_duration_non_peak):
    return high_duration_peak if hour in peak_hours else low_duration_non_peak

# Traffic Responsive Control Algorithm
def traffic_responsive_control(traffic_volume, threshold, high_duration, medium_duration):
    return high_duration if traffic_volume > threshold else medium_duration

# Queue Length Based Control Algorithm
def queue_length_based_control(traffic_volume, high_threshold, low_threshold, high_duration, medium_duration, low_duration):
    if traffic_volume > high_threshold:
        return high_duration
    elif traffic_volume < low_threshold:
        return low_duration
    else:
        return medium_duration

def hybrid_algorithm_1(hour, traffic_volume, peak_hours, high_duration_peak, low_duration_non_peak, threshold, high_duration, medium_duration, vehicle_pass_rate):
    if hour in peak_hours:
        return fixed_time_control(hour, peak_hours, high_duration_peak, low_duration_non_peak)
    else:
        return traffic_responsive_control(traffic_volume, threshold, high_duration, medium_duration)

def hybrid_algorithm_2(hour, traffic_volume, peak_hours, high_threshold, low_threshold, high_duration, medium_duration, low_duration, threshold, high_duration_resp, medium_duration_resp, vehicle_pass_rate):
    if hour in peak_hours:
        return queue_length_based_control(traffic_volume, high_threshold, low_threshold, high_duration, medium_duration, low_duration)
    else:
        return traffic_responsive_control(traffic_volume, threshold, high_duration_resp, medium_duration_resp)
        
def simulate_control(hour, traffic_volume, control_type, peak_hours, high_duration_peak, low_duration_non_peak, traffic_threshold, high_threshold, low_threshold, high_duration, medium_duration, low_duration, vehicle_pass_rate):
    if control_type == 'Fixed-Time Control':
        green_duration = fixed_time_control(hour, peak_hours, high_duration_peak, low_duration_non_peak)
    elif control_type == 'Traffic Responsive Control':
        green_duration = traffic_responsive_control(traffic_volume, traffic_threshold, high_duration, medium_duration)
    elif control_type ==  'Queue Length Based Control':
        green_duration = queue_length_based_control(traffic_volume, high_threshold, low_threshold, high_duration, medium_duration, low_duration)
    elif control_type == 'Hybrid Algorithm 1':
        green_duration = hybrid_algorithm_1(hour, traffic_volume, peak_hours, high_duration_peak, low_duration_non_peak, traffic_threshold, high_duration, medium_duration, vehicle_pass_rate)
    else:  # Hybrid Algorithm 2
        green_duration = hybrid_algorithm_2(hour, traffic_volume, peak_hours, high_threshold, low_threshold, high_duration, medium_duration, low_duration, traffic_threshold, high_duration, medium_duration, vehicle_pass_rate)

    print(f"{control_type} - Hour: {hour}, Traffic Volume: {traffic_volume}, Green Duration: {green_duration}")

    vehicles_passed_per_hour = green_duration * vehicle_pass_rate
    if vehicles_passed_per_hour < traffic_volume:
    # Calculate time based on how many vehicles can pass in an hour
        time_to_clear_traffic = 60  # Since not all vehicles can pass in an hour
    else:
    # Calculate time based on how long it takes to clear the given volume of traffic
        time_to_clear_traffic = (traffic_volume / vehicles_passed_per_hour) * 60
    return time_to_clear_traffic / 60  # Convert to minutes




# Function to plot the results
def plot_results(road_segment, date, clearance_times_by_algorithm):
    hours = range(24)
    plt.figure(figsize=(12, 6))
    for algorithm_name, clearance_times in clearance_times_by_algorithm.items():
        plt.plot(hours, clearance_times, label=algorithm_name)

    plt.title(f"Traffic Clearance Time for {road_segment} on {date}")
    plt.xlabel("Hour of Day")
    plt.ylabel("Clearance Time (in minutes)")
    plt.legend()
    plt.grid(True)
    plt.show()
    
def main():
    file_path = 'traffic-volume-counts-1.csv'
    traffic_data, hourly_traffic_columns = load_and_preprocess_data(file_path)
    print("Data Loaded and Preprocessed")

    # Define parameters
    peak_hours = set([7, 8, 9, 16, 17, 18])
    high_duration_peak = 180  # Longer green light duration for peak hours
    low_duration_non_peak = 60  # Shorter green light duration for non-peak hours
    traffic_threshold = 50  # Threshold for Traffic Responsive Control
    high_threshold = 75    # High threshold for Queue Length Based Control
    low_threshold = 25     # Low threshold for Queue Length Based Control
    high_duration = 150    # Longer green light duration for high traffic
    medium_duration = 90   # Medium green light duration
    low_duration = 45      # Shorter green light duration for low traffic
    vehicle_pass_rate = 2  # Moderated vehicle pass rate

    # Compare algorithms on each road segment for each date and plot results
    algorithms = ['Fixed-Time Control', 'Traffic Responsive Control', 'Queue Length Based Control', 'Hybrid Algorithm 1', 'Hybrid Algorithm 2']
    for (roadway, from_, to, direction), group in traffic_data.groupby(['Roadway Name', 'From', 'To', 'Direction']):
        road_segment = f"{roadway} from {from_} to {to} ({direction})"
        for date, date_traffic_data in group.groupby('Date'):
            hourly_traffic = date_traffic_data[hourly_traffic_columns].mean()
            print(f"\nRoad Segment: {road_segment}, Date: {date}")
            print("Hourly Traffic Volumes:", hourly_traffic)

            clearance_times_by_algorithm = {}
            for algorithm in algorithms:
                clearance_times = [simulate_control(hour, vol, algorithm, peak_hours, high_duration_peak, low_duration_non_peak, traffic_threshold, high_threshold, low_threshold, high_duration, medium_duration, low_duration, vehicle_pass_rate) for hour, vol in enumerate(hourly_traffic)]
                clearance_times_by_algorithm[algorithm] = clearance_times
                print(f"{algorithm} Clearance Times:", clearance_times)
                
            plot_results(road_segment, date, clearance_times_by_algorithm)
            clearance_times_by_algorithm = {}



if __name__ == "__main__":
    main()