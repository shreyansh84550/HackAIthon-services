import json
from datetime import datetime
from collections import defaultdict
 
def parse_date(date_str):
    """Parse various date formats including with time components"""
    if not date_str:
        return None
   
    # Handle Vietnamese date prefixes
    date_str = date_str.lower()
    for prefix in ["ngày", "nam", "năm"]:
        if date_str.startswith(prefix):
            date_str = date_str[len(prefix):].strip()
   
    try:
        # Try ISO format first (2024-04-18 00:00:00)
        return datetime.strptime(date_str.split()[0], '%Y-%m-%d')
    except ValueError:
        try:
            # Try day/month/year format (18/04/2024)
            return datetime.strptime(date_str.split()[0], '%d/%m/%Y')
        except ValueError:
            try:
                # Try year-only format
                if len(date_str) == 4 and date_str.isdigit():
                    return datetime.strptime(date_str, '%Y')
            except:
                return None
    return None
 
def detect_anomalies(data):
    anomalies = []
   
    # Extract basic trip info with date parsing
    trip_id = data.get('tripId', 'unknown')
    member_count = int(data.get('memberCount', 0)) if data.get('memberCount') else 0
    from_date = parse_date(data.get('fromDate'))
    to_date = parse_date(data.get('toDate'))
   
    # Face count analysis
    face_counts = []
    group_photo_files = []
   
    # Bill analysis
    bill_dates = []
    bill_amounts = []
    has_bills = False  # Track if we found any bill evidence
   
    # Process all evidence (including nested in classification)
    evidence_sources = []
   
    # Check main evidences if exists
    if 'evidences' in data:
        evidence_sources.append(data['evidences'])
   
    # Check classification.extracted_entities if exists
    if 'classfication' in data and 'extracted_entities' in data['classfication']:
        for entity_group in data['classfication']['extracted_entities']:
            if isinstance(entity_group, list):
                evidence_sources.append(entity_group)
   
    # Process all evidence sources
    for evidence_group in evidence_sources:
        for evidence in evidence_group:
            if not evidence:  # Skip null entries
                continue
               
            # Group photo analysis
            if evidence.get('type') in ['group-photo', 'group_photo']:
                group_photo_files.append(evidence.get('file', 'unknown'))
                if evidence.get('image_analysis') is not None:  # Check for None first
                    face_count = evidence['image_analysis'].get('no_of_faces_detected', 0)
                    face_counts.append(face_count)
                else:
                    anomalies.append({
                        'rule': 'missing_image_analysis',
                        'tripId': trip_id,
                        'file': evidence.get('file', 'unknown'),
                        'message': "Group photo has no image analysis data"
                    })
           
            # Bill analysis
            elif evidence.get('type') == 'bill':
                has_bills = True  # We found bill evidence
                if 'processing_results' in evidence:
                    for entity in evidence['processing_results'].get('entities', []):
                        if entity.get('type') == 'bill-date':
                            bill_date = parse_date(entity.get('mentionText'))
                            if bill_date:
                                bill_dates.append({
                                    'date': bill_date,
                                    'confidence': entity.get('confidence', 0),
                                    'source': evidence.get('file', 'unknown')
                                })
                       
                        if entity.get('type') == 'bill-amount':
                            bill_amounts.append({
                                'amount': entity.get('mentionText', ''),
                                'confidence': entity.get('confidence', 0),
                                'source': evidence.get('file', 'unknown')
                            })
   
    # Rule 1: Member count validation
    if face_counts:
        max_faces = max(face_counts)
        min_faces = min(face_counts)
        exact_match = member_count in face_counts
       
        if not exact_match:
            if member_count < min_faces:
                anomalies.append({
                    'rule': 'member_count_too_low',
                    'tripId': trip_id,
                    'memberCount': member_count,
                    'minFacesDetected': min_faces,
                    'allFaceCounts': face_counts,
                    'groupPhotoFiles': group_photo_files,
                    'message': f"Member count {member_count} is less than minimum faces detected {min_faces} in group photos"
                })
            elif member_count > max_faces:
                anomalies.append({
                    'rule': 'member_count_too_high',
                    'tripId': trip_id,
                    'memberCount': member_count,
                    'maxFacesDetected': max_faces,
                    'allFaceCounts': face_counts,
                    'groupPhotoFiles': group_photo_files,
                    'message': f"Member count {member_count} is more than maximum faces detected {max_faces} in group photos"
                })
    elif group_photo_files:  # We have group photos but no face counts
        anomalies.append({
            'rule': 'no_face_detection',
            'tripId': trip_id,
            'memberCount': member_count,
            'groupPhotoFiles': group_photo_files,
            'message': "Group photos found but no face detection data available"
        })
    else:
        anomalies.append({
            'rule': 'no_group_photos',
            'tripId': trip_id,
            'memberCount': member_count,
            'message': "No group photos found to validate member count"
        })
   
    # Rule 2: Trip dates vs bill dates (only if we have dates)
    if from_date and to_date:
        valid_bill_dates = []
        invalid_bill_dates = []
       
        for bill in bill_dates:
            if bill['confidence'] > 0.5:  # Only consider confident detections
                if from_date <= bill['date'] <= to_date:
                    valid_bill_dates.append(bill)
                else:
                    invalid_bill_dates.append(bill)
       
        # Report all invalid bill dates
        for bill in invalid_bill_dates:
            anomalies.append({
                'rule': 'bill_date_out_of_range',
                'tripId': trip_id,
                'tripDates': f"{from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}",
                'billDate': bill['date'].strftime('%Y-%m-%d'),
                'confidence': bill['confidence'],
                'source': bill['source'],
                'message': "Bill date outside trip date range"
            })
       
        # Modified condition to check for bills without dates
        if has_bills and not bill_dates:
            anomalies.append({
                'rule': 'no_bill_dates_found',
                'tripId': trip_id,
                'message': "Bills found but no dates could be extracted from them"
            })
        elif has_bills and bill_dates and not valid_bill_dates:
            anomalies.append({
                'rule': 'no_valid_bill_dates',
                'tripId': trip_id,
                'message': "No bills found within trip date range"
            })
    elif has_bills and (not from_date or not to_date):
        anomalies.append({
            'rule': 'missing_trip_dates',
            'tripId': trip_id,
            'message': "Cannot validate bill dates - missing trip dates"
        })
   
    # Rule 3: Multiple high-confidence bill amounts (potential duplicates)
    high_conf_amounts = [b for b in bill_amounts if b['confidence'] > 0.8]
    if len(high_conf_amounts) > 3:
        anomalies.append({
            'rule': 'possible_duplicate_bills',
            'tripId': trip_id,
            'billCount': len(high_conf_amounts),
            'message': f"Found {len(high_conf_amounts)} high-confidence bill amounts"
        })
   
    return anomalies
 
# Example usage with error handling
def processJSONdetectAnamoly(JSONFile):
    with open(JSONFile) as f:
        trips = json.load(f)
    all_anomalies = []
    for trip in trips:
        try:
            anomalies = detect_anomalies(trip)
            if anomalies:
                all_anomalies.extend(anomalies)
        except Exception as e:
            print(f"Error processing trip {trip.get('tripId', 'unknown')}: {str(e)}")
   
    print(f"Found {len(all_anomalies)} anomalies across {len(trips)} trips")
    return all_anomalies