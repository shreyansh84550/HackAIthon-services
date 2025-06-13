import json
from datetime import datetime

def process_trip(trip_data):
    """Function to process individual trip data"""
    print(f"\nProcessing Trip ID: {trip_data['tripId']}")
    print(f"- Date: {trip_data['fromDate']} to {trip_data['toDate']}")
    print(f"- Evidence Folder: {trip_data['evidenceFolderPath']}")
    print(f"- Members: {trip_data['memberCount']}")
    
    # Convert string dates to datetime objects
    from_date = datetime.strptime(trip_data['fromDate'], '%Y-%m-%d %H:%M:%S')
    to_date = datetime.strptime(trip_data['toDate'], '%Y-%m-%d %H:%M:%S')
    
    # Convert member count to integer
    member_count = int(trip_data['memberCount'])
    
    #------------------------ Here is the logic that needs to be written -----------------------

    # You can add your custom processing logic here
    # For example: validate dates, check folder existence, etc.
    
    # Return processed data (modify as needed)
    return {
        'trip_id': trip_data['tripId'],
        'duration_days': (to_date - from_date).days,
        'evidence_path': trip_data['evidenceFolderPath'],
        'members': member_count
    }

def read_and_process_json(file_path):
    """Read JSON file and process each trip"""
    try:
        with open(file_path, 'r') as file:
            trips = json.load(file)
            
            if not isinstance(trips, list):
                print("Error: Expected a list of trips in JSON file")
                return []
                
            processed_trips = []
            for trip in trips:
                processed = process_trip(trip)
                processed_trips.append(processed)
                
            return processed_trips
            
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
        return []
    except KeyError as e:
        print(f"Error: Missing required field {e}")
        return []

# Example usage
if __name__ == "__main__":
    # Path to your JSON file
    json_file = "trips.json"
    
    # Read and process the JSON file
    results = read_and_process_json(json_file)
    
    # Print summary of processed trips
    print("\nProcessing Summary:")
    for result in results:
        print(f"Trip {result['trip_id']}: {result['members']} members, duration {result['duration_days']} days")