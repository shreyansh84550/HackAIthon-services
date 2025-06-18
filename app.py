import json
from flask import Flask, jsonify, request, render_template, redirect, url_for,jsonify, send_from_directory,abort
import os
from processInputFile import processUploadedFile
from readProcessJSON import read_and_process_json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx'}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_IMAGE_FOLDER = os.path.join(BASE_DIR)  

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Save the file to the upload folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        #Concat the filePath and the fileName
        fullFile = filepath + "/" + file.filename
        # Read file contents using the separate function
        processUploadedFile(filepath)
        print("This is the end!!!!")
        # Return the content to display on the frontend
        #return render_template('results.html', 
        #                     filename=file.filename, 
        #                     content=content,
        #                     content_type=type(content).__name__)
        return "This is end"
    return "Invalid file type"

@app.route('/processJSONFile', methods=['GET'])
def processJSONFile():
    # Check if the post request has the file part
    jsonFile = 'jsonFiles/' + str(request.args.get('jsonFile'))
    if not jsonFile:
            return {"error": "filename parameter is required"}, 400
    
    read_and_process_json(jsonFile)

    return {"message": f"Processing {jsonFile}", "status": "success"}

JSON_FOLDER = "jsonFiles"
@app.route('/get-list', methods=['GET'])
def getListOfTrips():
    trips = []
    try:
        # Iterate over each file in the folder
        for filename in os.listdir(JSON_FOLDER):
            if filename.endswith(".json"):
                file_path = os.path.join(JSON_FOLDER, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if isinstance(data, list) and len(data) == 2:
                        first_obj = data[0]
                        validation_obj = data[1]
                        # Move second object under "validation" key of the first
                        first_obj["validation"] = validation_obj
                        trips.append(first_obj)
                    elif isinstance(data, list):
                        # If it's a list with more than 1 object, flatten and keep each as separate
                        trips.extend(data)
                    else:
                        # If it's a single object (not a list)
                        trips.append(data)  # Append data from each file
                        
        sorted_trips = sorted(
            trips,
            key=lambda trip: (
                1 if trip.get("classfication", {}).get("status") else 0,
                str(trip.get("classfication", {}).get("status", "")).lower()
            )
        )
        return jsonify(sorted_trips)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-trip-detail-by-id/<tripId>', methods=['GET'])
def getTripDetailsById(tripId):
    trips = []
    try:
        file_path = os.path.join(JSON_FOLDER, f"{tripId}.json")

        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({"error": f"Trip ID {tripId} not found"}), 404

        # Read the file and return its content
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list) and len(data) == 2:
                first_obj = data[0]
                validation_obj = data[1]
                # Move second object under "validation" key of the first
                first_obj["validation"] = validation_obj
                trips.append(first_obj)
            elif isinstance(data, list):
                # If it's a list with more than 1 object, flatten and keep each as separate
                trips.extend(data)
            else:
                # If it's a single object (not a list)
                trips.append(data) 

        return jsonify(trips)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/preview/<path:filename>')
def preview_file(filename):
    full_path = os.path.join(BASE_IMAGE_FOLDER, filename)
    if os.path.isfile(full_path):
        folder = os.path.dirname(filename)
        file = os.path.basename(filename)
        return send_from_directory(os.path.join(BASE_IMAGE_FOLDER, folder), file)
    else:
        return abort(404)    

if __name__ == '__main__':
    app.run(debug=True)
