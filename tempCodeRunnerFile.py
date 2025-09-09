import face_recognition
import os
import numpy as np

# --- Configuration ---
# Folders where the images are stored
TEACHER_FOLDER = 'uploads'
STUDENT_FOLDER = 'data'
RESULTS_FOLDER = 'results' # Folder to save the output report

# The tolerance for face comparison. Lower is stricter. 0.55 is a good balance.
TOLERANCE = 0.55

def load_known_students(student_folder_path):
    """
    Loads all student images and their data from the 'data' folder.
    Returns two lists: one with face encodings and one with corresponding student info.
    """
    known_face_encodings = []
    known_student_data = []

    print("Loading known student data...")
    # Loop through each file in the student folder
    for filename in os.listdir(student_folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Construct full file paths
            image_path = os.path.join(student_folder_path, filename)
            info_path = os.path.join(student_folder_path, os.path.splitext(filename)[0] + '.txt')

            # Check if the corresponding .txt file exists
            if os.path.exists(info_path):
                try:
                    # Load the student's image and get face encoding
                    student_image = face_recognition.load_image_file(image_path)
                    
                    # This assumes each student image has only ONE face.
                    student_face_encodings = face_recognition.face_encodings(student_image)
                    
                    if not student_face_encodings:
                        print(f"Warning: No face found in {filename}. Skipping.")
                        continue
                        
                    student_encoding = student_face_encodings[0]

                    # Read student's name and ID from the text file
                    with open(info_path, 'r') as f:
                        student_info = {}
                        for line in f:
                            if ':' in line:
                                key, value = line.strip().split(':', 1)
                                student_info[key.strip()] = value.strip()
                    
                    # Store the encoding and the student's data
                    known_face_encodings.append(student_encoding)
                    known_student_data.append(student_info)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
            else:
                print(f"Warning: No .txt file found for {filename}. Skipping.")
    
    print(f"Loaded {len(known_student_data)} known students.")
    return known_face_encodings, known_student_data

def find_present_students(class_photo_path, known_encodings, known_data):
    """
    Finds all faces in the class photo and identifies which known students are present.
    """
    present_students = []
    
    print(f"\nProcessing class photo: {os.path.basename(class_photo_path)}")
    
    try:
        # Load the class photo
        class_image = face_recognition.load_image_file(class_photo_path)
        
        # Find all face locations using the more accurate CNN model for better accuracy
        unknown_face_locations = face_recognition.face_locations(class_image, model="cnn")
        unknown_face_encodings = face_recognition.face_encodings(class_image, unknown_face_locations)
        
        print(f"Found {len(unknown_face_encodings)} face(s) in the class photo.")

        # Loop through each face found in the class photo
        for unknown_encoding in unknown_face_encodings:
            # Compare this face with all known student faces
            matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=TOLERANCE)
            
            # Find the best match if one exists
            face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                matched_student_data = known_data[best_match_index]
                # Avoid adding duplicates
                if matched_student_data not in present_students:
                    present_students.append(matched_student_data)

    except Exception as e:
        print(f"Could not process the class photo. Error: {e}")
        
    return present_students


if __name__ == "__main__":
    # Create the results folder if it doesn't exist
    if not os.path.exists(RESULTS_FOLDER):
        os.makedirs(RESULTS_FOLDER)

    # 1. Load the data for all known students
    known_encodings, known_data = load_known_students(STUDENT_FOLDER)

    # Check if there are any known students to compare against
    if not known_encodings:
        print("No student data loaded. Please check the 'data' folder.")
    else:
        # 2. Find the teacher's class photo to process
        # This script assumes we process the FIRST image found in the 'uploads' folder.
        class_photo_file = None
        for filename in os.listdir(TEACHER_FOLDER):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                class_photo_file = os.path.join(TEACHER_FOLDER, filename)
                break # Stop after finding the first image

        if class_photo_file:
            # 3. Find and identify students in the class photo
            attendance_list = find_present_students(class_photo_file, known_encodings, known_data)
            
            # 4. Print the final results to the console
            print("\n--- Attendance Result ---")
            if attendance_list:
                print("The following students were found in the class photo:")
                for student in attendance_list:
                    name = student.get('Name', 'N/A')
                    unique_id = student.get('Roll No', 'N/A')
                    print(f" - Name: {name}, Unique ID: {unique_id}")

                # 5. Save the results to a new text file
                report_path = os.path.join(RESULTS_FOLDER, 'attendance_report.txt')
                with open(report_path, 'w') as f:
                    f.write("--- Attendance Report ---\n")
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

