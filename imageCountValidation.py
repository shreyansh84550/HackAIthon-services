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
 
def detect_faces(image_path):
    service_account_info = {
        # Paste your service account info here
        "type": "service_account",
        "project_id": "aerobic-coast-461806-a7",
        "private_key_id": "409e391e4ddecd2550d6a26aae4ddcec24b1e6af",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDbflaabeMKGc5h\nJoqgkDpAp8tO2Y9A/jw25mEiCgxnf+mxTmMzj38iUzKXgrj1wfif+j9KqibBGkkB\nM7ri7msKaVOMYunnkF7s54PxR69n3lOd9Z/B8hu4OfptqgsAYT4ZwSuTieSfcsD/\nyQk3hjX81xZoinXD9z/aLq9PeUhgJgOKnFteQ4jol6i7Ws5L8aFEyWPvvInXHMg+\n6SKitMiPsAPUS+iE8R1n3bfHtPiAS9zYCshjkh4mldFT+2rVxS3/Jzb5QbAB54fx\nIu167YS1X09EcE6t/DhzWTRVsSdXJvr+t8rdaHtuyJgB0/lwAPx7X+xVE+Hs9RjW\nVzRsFd3LAgMBAAECggEAS6JKR2asQJPJ6PI1/MQWPqdTSHVxhqzUpPpX6DncMmIC\nbiWby22cGoDewxS5lX3kpYO/AYSGXC4pj+96a65KVkkbEBoZjcDS5QGWFrNj/v++\ngoTcKyG5aY8Y+2cH6XaYxpko4es3S7ZoSPvGYEqwGdMoFpf3orJ1X0KNCG67gN2V\nJUnLOnr18yVwtvPZH2ucsqNtDLXse4knD8NCWLug/YroBzfgKzuJSbaHHZ2JrO8k\nvzRF0bPxUhjqAzUhv78Wh8r4q+djk3+Gl4de9q9CFr7dLX7Q3NfTPjLuZEwyFmLv\nbVHi/r2Xvljk46nTIoV8XmLV9878vXCduuA5gkp8+QKBgQDvOsicLVaN9kS0+moN\nc526ENOmOppfjYc6Czwb5n77VEju7FqXtsIOmq8qWGxHANcHPPwH7pqiDx3JPcC2\n4x5lRMGEIAqt6ETW2n2UQWdaJv/hvtTAzC+N3sEzl5608GlDsxdvVzu5vyUO3bSE\n1RnIzxScB2wBXjLQVPvB1vhp1wKBgQDq4V7Gy2BDGUgDuLoRWZg/DcdtBEI+Z0+s\ngPvGpzGNyGC6IFFFKYJ5JxP+iC6BBRwCaa2Olx0EkJovgw2Ke3eREeTTf1qhtjTm\n5k9NkhnMCW+9uyimHGA8pN7HJze/yQvYdifF+ReWPGyZVXi3ldoCDpYDfrIVrFGu\nYyiirNR1LQKBgGbuXf6Eq2ctfOZ5kEP1aPnz33z4Xg+a74IT72r5w80TuMXEQD5i\nziBGgfOwU/ZA8EQXA0HOcg4kfuZlgZOvKRbdfH4C41VsSKJBJCMz+OobOaHB3/yM\nXjGmlG5EYG7tufz9A6pOWE5VZfZ9gfxdTFjQcMepkdkM1MQ6rI/8lKnFAoGBAIQD\npcRwHKu58ur8kcAcrmCKOxN/+Eegw3w+hsSxxj1daVhTv7nyyb2UhD1kh1bG62ZD\nxWPGdW3SZIbdzueN27cy6n0hMGyBv5wjyGDeBBfVGfP21LMAcerD897VoRTvR/Qi\n/Nnd1i7/yT4pdw8gb4cGcbSHKkraLpKocvdz0noFAoGATWYjUsW5bSiYOsqYlxtq\nJEH3dAGJpMJVpW98LHzNo6qmIfOPdK7sQcVMpi7m+qObH10FwZCvIIQ8hGEjcm/y\nA6gkYVYMRywzh0qusxSd05SDzVqGL21yZK9tQb5YAOt7sURlgbludkiGHaDyZJqK\n1zoM7QpLI34DxqPsypHnLfk=\n-----END PRIVATE KEY-----\n",
        "client_email": "google-cloud-vision-quickstart@aerobic-coast-461806-a7.iam.gserviceaccount.com",
        "client_id": "112797123836256308699",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    
    """Detect faces using Google Vision API with service account auth."""
    try:
        # Get access token
        access_token = get_access_token(service_account_info)
        
        # Read and encode image
        with open(image_path, "rb") as image_file:
            content = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Prepare request - corrected "FACE_DETECTION" spelling and added maxResults
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "requests": [{
                "image": {"content": content},
                "features": [{
                    "type": "FACE_DETECTION",  # Corrected from "FACE_DETECTION"
                    "maxResults": 50  # Added to get more results
                }]
            }]
        }
        
        # Make request
        response = requests.post(
            "https://vision.googleapis.com/v1/images:annotate",
            headers=headers,
            json=body,
            timeout=30  # Added timeout
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        print(f"Error in detect_faces: {str(e)}")
        return {'error': {'message': str(e)}}
 
def count_faces(api_response):
    """Count the number of faces detected in the API response."""
    # First check if the API returned an error
    if 'error' in api_response:
        print(f"API Error: {api_response['error']['message']}")
        return 0
    
    # Corrected spelling from 'responses' to 'responses'
    if not api_response.get('responses', []):
        print("No responses found in API result")
        return 0
    
    # Get the first response
    first_response = api_response['responses'][0]
    
    # Check if face detection failed for this image
    if 'error' in first_response:
        print(f"Face detection error: {first_response['error']['message']}")
        return 0
    
    # Get face annotations or empty list if none exist
    face_annotations = first_response.get('faceAnnotations', [])
    
    # Debug print to see what's being detected
    print(f"Face detection details: {json.dumps(face_annotations, indent=2)}")
    
    return len(face_annotations)
 
 
# Example usage
if __name__ == "__main__":
    # Load your service account info (you can load from JSON file)
    service_account_info = {
        # Paste your service account info here
        "type": "service_account",
        "project_id": "aerobic-coast-461806-a7",
        "private_key_id": "409e391e4ddecd2550d6a26aae4ddcec24b1e6af",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDbflaabeMKGc5h\nJoqgkDpAp8tO2Y9A/jw25mEiCgxnf+mxTmMzj38iUzKXgrj1wfif+j9KqibBGkkB\nM7ri7msKaVOMYunnkF7s54PxR69n3lOd9Z/B8hu4OfptqgsAYT4ZwSuTieSfcsD/\nyQk3hjX81xZoinXD9z/aLq9PeUhgJgOKnFteQ4jol6i7Ws5L8aFEyWPvvInXHMg+\n6SKitMiPsAPUS+iE8R1n3bfHtPiAS9zYCshjkh4mldFT+2rVxS3/Jzb5QbAB54fx\nIu167YS1X09EcE6t/DhzWTRVsSdXJvr+t8rdaHtuyJgB0/lwAPx7X+xVE+Hs9RjW\nVzRsFd3LAgMBAAECggEAS6JKR2asQJPJ6PI1/MQWPqdTSHVxhqzUpPpX6DncMmIC\nbiWby22cGoDewxS5lX3kpYO/AYSGXC4pj+96a65KVkkbEBoZjcDS5QGWFrNj/v++\ngoTcKyG5aY8Y+2cH6XaYxpko4es3S7ZoSPvGYEqwGdMoFpf3orJ1X0KNCG67gN2V\nJUnLOnr18yVwtvPZH2ucsqNtDLXse4knD8NCWLug/YroBzfgKzuJSbaHHZ2JrO8k\nvzRF0bPxUhjqAzUhv78Wh8r4q+djk3+Gl4de9q9CFr7dLX7Q3NfTPjLuZEwyFmLv\nbVHi/r2Xvljk46nTIoV8XmLV9878vXCduuA5gkp8+QKBgQDvOsicLVaN9kS0+moN\nc526ENOmOppfjYc6Czwb5n77VEju7FqXtsIOmq8qWGxHANcHPPwH7pqiDx3JPcC2\n4x5lRMGEIAqt6ETW2n2UQWdaJv/hvtTAzC+N3sEzl5608GlDsxdvVzu5vyUO3bSE\n1RnIzxScB2wBXjLQVPvB1vhp1wKBgQDq4V7Gy2BDGUgDuLoRWZg/DcdtBEI+Z0+s\ngPvGpzGNyGC6IFFFKYJ5JxP+iC6BBRwCaa2Olx0EkJovgw2Ke3eREeTTf1qhtjTm\n5k9NkhnMCW+9uyimHGA8pN7HJze/yQvYdifF+ReWPGyZVXi3ldoCDpYDfrIVrFGu\nYyiirNR1LQKBgGbuXf6Eq2ctfOZ5kEP1aPnz33z4Xg+a74IT72r5w80TuMXEQD5i\nziBGgfOwU/ZA8EQXA0HOcg4kfuZlgZOvKRbdfH4C41VsSKJBJCMz+OobOaHB3/yM\nXjGmlG5EYG7tufz9A6pOWE5VZfZ9gfxdTFjQcMepkdkM1MQ6rI/8lKnFAoGBAIQD\npcRwHKu58ur8kcAcrmCKOxN/+Eegw3w+hsSxxj1daVhTv7nyyb2UhD1kh1bG62ZD\nxWPGdW3SZIbdzueN27cy6n0hMGyBv5wjyGDeBBfVGfP21LMAcerD897VoRTvR/Qi\n/Nnd1i7/yT4pdw8gb4cGcbSHKkraLpKocvdz0noFAoGATWYjUsW5bSiYOsqYlxtq\nJEH3dAGJpMJVpW98LHzNo6qmIfOPdK7sQcVMpi7m+qObH10FwZCvIIQ8hGEjcm/y\nA6gkYVYMRywzh0qusxSd05SDzVqGL21yZK9tQb5YAOt7sURlgbludkiGHaDyZJqK\n1zoM7QpLI34DxqPsypHnLfk=\n-----END PRIVATE KEY-----\n",
        "client_email": "google-cloud-vision-quickstart@aerobic-coast-461806-a7.iam.gserviceaccount.com",
        "client_id": "112797123836256308699",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
   
   # try:
   #     result = detect_faces("group-photos/1713774178156_63ced062-35ed-4272-b6d6-05a959119ab4.jpg", service_account_info)
   #     face_count = count_faces(result)
   #     print("No of persons in the group ",face_count)
   # except Exception as e:
   #     print("Error:", str(e))