import os
import json
from datetime import datetime
from typing import List, Dict
from processFolder import process_files_in_folder

def read_and_process_json(json_folder):
    """
    Scan through a folder containing JSON files with trip data, process each trip,
    and update the original JSON files with the processed results.
    
    Args:
        json_folder: Path to folder containing JSON trip files
        
    Returns:
        List of all processed trips with their extracted entities
    """
    all_processed_trips = []
    
    if not os.path.exists(json_folder):
        print(f"Error: JSON folder not found at {json_folder}")
        return all_processed_trips
    
    for json_file in os.listdir(json_folder):
        if not json_file.lower().endswith('.json'):
            continue
            
        file_path = os.path.join(json_folder, json_file)
        print(f"\nProcessing JSON file: {json_file}")
        
        try:
            with open(file_path, 'r') as f:
                trips = json.load(f)
                
                if not isinstance(trips, list):
                    print(f"Error in {json_file}: Expected a list of trips")
                    continue
                
                processed_trips = []
                for trip in trips:
                    processed_trip = process_trip(trip)
                    processed_trips.append(processed_trip)
                    all_processed_trips.append(processed_trip)
                
                # Write the processed data back to the same file
                with open(file_path, 'w') as f:
                    json.dump(processed_trips, f, indent=2)
                print(f"Updated {json_file} with processed data")
                    
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            continue
            
    return all_processed_trips

def process_trip(trip_data: Dict) -> Dict:
    """Process individual trip data including its evidence files"""
    print(f"\nProcessing Trip ID: {trip_data['tripId']}")
    
    try:
        # Convert and validate dates
        from_date = datetime.strptime(trip_data['fromDate'], '%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(trip_data['toDate'], '%Y-%m-%d %H:%M:%S')
        member_count = int(trip_data['memberCount'])
        
        # Process evidence files
        evidence_folder = trip_data['evidenceFolderPath']
        #Classify if the file is Bill/group-photo/booking
        entities = process_files_in_folder(evidence_folder)
        
        # Create the processed trip object (including original data plus processing results)
        processed_trip = {
            **trip_data,  # Include all original data
            'evidenceVerification': {
                'duration_days': (to_date - from_date).days,
                'extracted_entities': entities,
                'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'success'
            }
        }
        
        return processed_trip
        
    except KeyError as e:
        print(f"Missing required field in trip data: {e}")
        return {
            **trip_data,
            'processed': {
                'status': 'error',
                'error': f"Missing field: {e}",
                'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
    except Exception as e:
        print(f"Error processing trip {trip_data.get('tripId', 'unknown')}: {e}")
        return {
            **trip_data,
            'processed': {
                'status': 'error',
                'error': str(e),
                'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }