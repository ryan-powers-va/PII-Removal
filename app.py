from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
import os
from script import remove_pii_from_excel 

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route to serve files from the uploads directory
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/")
def index():
    return render_template("index.html")  # Serves the HTML page for the app

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded file
    input_file = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_file)

    # Process the file
    output_file = input_file.replace(".xlsx", "_cleaned.xlsx")
    try:
        remove_pii_from_excel(input_file, output_file)
        return jsonify({"success": True, "output_file": output_file}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
