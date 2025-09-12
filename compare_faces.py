import face_recognition
import os
import numpy as np
import datetime

# --- IMPORTANT: Your whatsapp.py file must be in the same folder ---
from whatsapp import send_whatsapp_notification 

# --- Configuration ---
TEACHER_FOLDER = 'uploads'
STUDENT_FOLDER = 'data'
RESULTS_FOLDER = 'results'
TOLERANCE = 0.55 # Lower is stricter, 0.6 is default, 0.55 is a bit stricter.

def load_student_info(file_path):
    """Reads a student's .txt file and returns their information as a dictionary."""
    student_info = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    student_info[key.strip()] = value.strip()
    except FileNotFoundError:
        return None
    return student_info

def load_known_students(student_folder_path):
    """Loads all student images and their data from the 'data' folder."""
    known_face_encodings = []
    known_student_data = []
    print("Loading known student data...")
    for filename in os.listdir(student_folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(student_folder_path, filename)
            info_path = os.path.join(student_folder_path, os.path.splitext(filename)[0] + '.txt')
            
            if os.path.exists(info_path):
                try:
                    student_image = face_recognition.load_image_file(image_path)
                    student_face_encodings = face_recognition.face_encodings(student_image)
                    if not student_face_encodings:
                        print(f"Warning: No face found in {filename}. Skipping.")
                        continue
                    
                    student_encoding = student_face_encodings[0]
                    student_info = load_student_info(info_path)
                    
                    if student_info:
                        known_face_encodings.append(student_encoding)
                        known_student_data.append(student_info)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
            else:
                print(f"Warning: No .txt file found for {filename}. Skipping.")
    print(f"Loaded {len(known_student_data)} known students.")
    return known_face_encodings, known_student_data

# <<< COPY FROM HERE >>>
def find_present_students(class_photo_path, known_encodings, known_data):
    """Finds and identifies all known students in the class photo."""
    present_students = []
    print(f"\nProcessing class photo: {os.path.basename(class_photo_path)}")
    try:
        class_image = face_recognition.load_image_file(class_photo_path)
        unknown_face_locations = face_recognition.face_locations(class_image, model="hog")
        unknown_face_encodings = face_recognition.face_encodings(class_image, unknown_face_locations)
        print(f"Found {len(unknown_face_encodings)} face(s) in the class photo.")

        for unknown_encoding in unknown_face_encodings:
            matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=0.55)
            face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                matched_student_data = known_data[best_match_index]
                
                # This debug line will show us the exact data read from the .txt file
                print(f"DEBUG: Matched student data dictionary: {matched_student_data}")

                if matched_student_data not in present_students:
                    present_students.append(matched_student_data)

                    # --- WHATSAPP NOTIFICATION LOGIC ---
                    student_name = matched_student_data.get('Name')
                    student_phone = matched_student_data.get('Phone No') 
                    
                    if student_name and student_phone:
                        print(f"SUCCESS: Phone number found for {student_name}. Sending notification...")
                        # This calls the function in your other file
                        send_whatsapp_notification(student_name, student_phone, "Data Structures")
                    else:
                        print(f"INFO: Notification not sent for {student_name} because phone number was not found in the dictionary.")
                    # --- END OF WHATSAPP LOGIC ---

    except Exception as e:
        print(f"Could not process the class photo. Error: {e}")
    return present_students
# <<< COPY UNTIL HERE >>>


if __name__ == "__main__":
    if not os.path.exists(RESULTS_FOLDER):
        os.makedirs(RESULTS_FOLDER)

    known_encodings, known_data = load_known_students(STUDENT_FOLDER)

    if not known_encodings:
        print("No student data loaded. Please check the 'data' folder.")
    else:
        # Find the first image in the uploads folder to process as the class photo
        class_photo_file = None
        for filename in sorted(os.listdir(TEACHER_FOLDER)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                class_photo_file = os.path.join(TEACHER_FOLDER, filename)
                break 

        if class_photo_file:
            attendance_list = find_present_students(class_photo_file, known_encodings, known_data)
            
            print("\n--- Attendance Result ---")
            if attendance_list:
                print("The following students were found in the class photo:")
                for student in attendance_list:
                    name = student.get('Name', 'N/A')
                    unique_id = student.get('Roll No', 'N/A')
                    print(f" - Name: {name}, Unique ID: {unique_id}")

                # Make the report filename unique with a timestamp to avoid overwriting
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                report_path = os.path.join(RESULTS_FOLDER, f'attendance_report_{timestamp}.txt')
                
                with open(report_path, 'w') as f:
                    f.write(f"--- Attendance Report ({timestamp}) ---\n")
                    f.write(f"Processed from photo: {os.path.basename(class_photo_file)}\n\n")
                    f.write("Present Students:\n")
                    for student in attendance_list:
                        name = student.get('Name', 'N/A')
                        unique_id = student.get('Roll No', 'N/A')
                        f.write(f" - Name: {name}, Unique ID: {unique_id}\n")
                
                print(f"\nReport saved successfully to: {report_path}")
            else:
                print("No known students were recognized in the photo.")
        else:
            print("No class photo found in the 'uploads' folder.")
            