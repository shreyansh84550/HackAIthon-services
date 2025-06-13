import base64
import json
import time
import requests
import jwt  # This is PyJWT

def get_access_token(service_account_info):
    """Generate an access token using service account credentials."""
    # Create signed JWT
    payload = {
        'iss': service_account_info['client_email'],
        'scope': 'https://www.googleapis.com/auth/cloud-vision',
        'aud': service_account_info['token_uri'],
        'exp': int(time.time()) + 3600,
        'iat': int(time.time())
    }
   
    # Sign the JWT
    signed_jwt = jwt.encode(
        payload,
        service_account_info['private_key'],
        algorithm='RS256',
        headers={'kid': service_account_info['private_key_id']}
    )
   
    # Exchange for access token
    response = requests.post(
        service_account_info['token_uri'],
        data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': signed_jwt
        }
    )
    return response.json()['access_token']

def detect_faces(image_path, service_account_info):
    """Detect faces using Google Vision API with service account auth."""
    try:
        # Get access token
        access_token = get_access_token(service_account_info)
       
        # Read and encode image
        with open(image_path, "rb") as image_file:
            content = base64.b64encode(image_file.read()).decode('utf-8')
       
        # Prepare request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "requests": [{
                "image": {"content": content},
                "features": [{"type": "FACE_DETECTION", "maxResults": 50}]  # Increased maxResults
            }]
        }
       
        # Make request
        response = requests.post(
            "https://vision.googleapis.com/v1/images:annotate",
            headers=headers,
            json=body
        )
        return response.json()
    except Exception as e:
        print(f"Error in detect_faces: {str(e)}")
        return {'error': {'message': str(e)}}

def count_faces(api_response):
    """Count the number of faces detected in the API response."""
    # First check for errors in the API response
    if 'error' in api_response:
        print(f"Vision API Error: {api_response['error']['message']}")
        return 0
    
    # Check if responses exists
    if not api_response.get('responses', []):
        return 0
    
    # Get the first response
    first_response = api_response['responses'][0]
    
    # Check for face detection errors
    if 'error' in first_response:
        print(f"Face Detection Error: {first_response['error']['message']}")
        return 0
    
    # Return the number of face annotations
    face_annotations = first_response.get('faceAnnotations', [])
    print(f"Face annotations: {json.dumps(face_annotations, indent=2)}")  # Debug output
    return len(face_annotations)
 
service_account_info = {
        "type": "service_account",
        "project_id": "aerobic-coast-461806-a7",
        "private_key_id": "409e391e4ddecd2550d6a26aae4ddcec24b1e6af",
        "private_key": "-----BEGIN PRIVATE KEY-----\n...",  # Your full private key here
        "client_email": "google-cloud-vision-quickstart@aerobic-coast-461806-a7.iam.gserviceaccount.com",
        "client_id": "112797123836256308699",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
