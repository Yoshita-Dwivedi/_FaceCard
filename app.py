import os
from flask import Flask, request, jsonify, render_template

# Initialize the Flask application
app = Flask(__name__)

# --- Define separate folders for teacher and student data ---
TEACHER_FOLDER = 'uploads'
STUDENT_FOLDER = 'data'

# Create the teacher uploads folder if it doesn't exist
if not os.path.exists(TEACHER_FOLDER):
    os.makedirs(TEACHER_FOLDER)

# Create the student data folder if it doesn't exist
if not os.path.exists(STUDENT_FOLDER):
    os.makedirs(STUDENT_FOLDER)


# --- Routes to Serve Your HTML Pages ---

@app.route('/')
def index():
    # Serve the teacher.html page by default
    return render_template('teacher.html')

@app.route('/teacher')
def teacher_page():
    return render_template('teacher.html')

@app.route('/student')
def student_page():
    return render_template('student.html')


# --- API Endpoint for Teacher Form ---

@app.route('/submit-teacher', methods=['POST'])
def submit_teacher():
    try:
        # Get text data from the form
        name = request.form['teacherName']
        institute = request.form['instituteName']
        subject = request.form['subject']
        
        # Get the image file
        image = request.files['classImage']

        if image:
            # Save the image to the 'uploads' folder
            image_path = os.path.join(TEACHER_FOLDER, image.filename)
            image.save(image_path)

            # Save the text data into a .txt file in the same folder
            info_filename = os.path.splitext(image.filename)[0] + '.txt'
            info_path = os.path.join(TEACHER_FOLDER, info_filename)
            with open(info_path, 'w') as f:
                f.write(f"Type: Teacher\n")
                f.write(f"Name: {name}\n")
                f.write(f"Institute: {institute}\n")
                f.write(f"Subject: {subject}\n")

            return jsonify({'success': True, 'message': 'Data saved successfully!'})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'})

# --- API Endpoint for Student Form ---

@app.route('/submit-student', methods=['POST'])
def submit_student():
    try:
        # Get text data from the form
        name = request.form['studentName']
        roll_no = request.form['rollNo']
        
        # Get the image file
        image = request.files['studentImage']

        if image:
            # *** MODIFIED: Save the image to the 'data' folder ***
            image_path = os.path.join(STUDENT_FOLDER, image.filename)
            image.save(image_path)

            # *** MODIFIED: Save the text data into a .txt file in the 'data' folder ***
            info_filename = os.path.splitext(image.filename)[0] + '.txt'
            info_path = os.path.join(STUDENT_FOLDER, info_filename)
            with open(info_path, 'w') as f:
                f.write(f"Type: Student\n")
                f.write(f"Name: {name}\n")
                f.write(f"Roll No: {roll_no}\n")
            
            return jsonify({'success': True, 'message': 'Data saved successfully!'})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'})

# --- Run the App ---

if __name__ == '__main__':
    # The host='0.0.0.0' makes the server accessible from your network
    app.run(host='0.0.0.0', port=5000, debug=True)
