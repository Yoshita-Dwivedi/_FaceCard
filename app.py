import os
import subprocess
import glob
import sys
from flask import Flask, request, jsonify, render_template

# Initialize the Flask application
app = Flask(__name__)

# --- Folder Paths ---
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
RESULTS_FOLDER = 'results'

# Create folders if they don't exist
for folder in [UPLOAD_FOLDER, DATA_FOLDER, RESULTS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER

# --- NEW: Get the correct Python executable from the venv ---
# This is the key to fixing the ModuleNotFoundError. It ensures
# the subprocess uses the same Python environment as the Flask app.
python_executable = sys.executable


# --- Routes to Serve Your HTML Pages ---

@app.route('/')
def index():
    return render_template('teacher.html')

@app.route('/teacher')
def teacher_page():
    return render_template('teacher.html')

@app.route('/student')
def student_page():
    return render_template('student.html')


# --- API Endpoints for Form Submissions ---

@app.route('/submit-teacher', methods=['POST'])
def submit_teacher():
    try:
        name = request.form['teacherName']
        institute = request.form['instituteName']
        subject = request.form['subject']
        image = request.files['classImage']

        if image and image.filename != '':
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)

            info_filename = os.path.splitext(image.filename)[0] + '.txt'
            info_path = os.path.join(app.config['UPLOAD_FOLDER'], info_filename)
            with open(info_path, 'w') as f:
                f.write(f"Type: Teacher\n")
                f.write(f"Name: {name}\n")
                f.write(f"Institute: {institute}\n")
                f.write(f"Subject: {subject}\n")

            return jsonify({'success': True, 'message': 'Data saved successfully!'})
        return jsonify({'success': False, 'message': 'No image selected.'})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'})

@app.route('/submit-student', methods=['POST'])
def submit_student():
    try:
        name = request.form['studentName']
        roll_no = request.form['rollNo']
        image = request.files['studentImage']

        if image and image.filename != '':
            image_path = os.path.join(app.config['DATA_FOLDER'], image.filename)
            image.save(image_path)
            
            info_filename = os.path.splitext(image.filename)[0] + '.txt'
            info_path = os.path.join(app.config['DATA_FOLDER'], info_filename)
            with open(info_path, 'w') as f:
                f.write(f"Type: Student\n")
                f.write(f"Name: {name}\n")
                f.write(f"Roll No: {roll_no}\n")
            
            return jsonify({'success': True, 'message': 'Data saved successfully!'})
        return jsonify({'success': False, 'message': 'No image selected.'})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'})

# --- API Endpoints for Attendance ---

@app.route('/run-attendance', methods=['POST'])
def run_attendance_script():
    """Runs the face comparison script using the correct venv Python."""
    print("Received request to run attendance script...")
    try:
        # ** THE FIX IS HERE **
        # Instead of just 'python', we use the full path to the python
        # executable that is running our Flask app (which is the one in the venv).
        result = subprocess.run(
            [python_executable, 'compare_faces.py'], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print("Script output:", result.stdout)
        return jsonify({'success': True, 'message': 'Attendance script completed successfully.'})
    except subprocess.CalledProcessError as e:
        print(f"Error running script: {e.stderr}")
        return jsonify({'success': False, 'message': f'Error running script: {e.stderr}'})
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'message': 'An unexpected server error occurred.'})

@app.route('/get-latest-report')
def get_latest_report():
    """Finds, reads, and returns the most recent attendance report."""
    try:
        list_of_files = glob.glob(os.path.join(RESULTS_FOLDER, '*.txt'))
        if not list_of_files:
            return jsonify({'success': False, 'report': 'No reports found.'})

        latest_file = max(list_of_files, key=os.path.getctime)
        
        with open(latest_file, 'r') as f:
            content = f.read()
            
        return jsonify({'success': True, 'report': content})
    except Exception as e:
        print(f"Error reading report: {e}")
        return jsonify({'success': False, 'report': 'Could not read the report file.'})

# --- Run the App ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

