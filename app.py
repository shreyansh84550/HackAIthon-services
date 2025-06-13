from flask import Flask, request, render_template, redirect, url_for
import os
from processInputFile import processUploadedFile
from readProcessJSON import read_and_process_json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx'}

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
if __name__ == '__main__':
    app.run(debug=True)
