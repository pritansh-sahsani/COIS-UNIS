from flask import render_template
from flask_login import current_user
from main.models import Student_details, User, Application

def allow_access(level="All"):
    if level != "All":
        if not current_user.is_authenticated:
            return render_template("/403.html")
        else:
            if level == "SUPERUSER":
                if current_user.username != "SUPERUSER":
                    return render_template("/403.html")
            elif level == "admins":
                if current_user.is_student:
                    return render_template("/403.html")
            elif level == "only_students":
                if not current_user.is_student:
                    return render_template("/403.html")
    return None

def GetAppAndAddNo(unis):
    no_add = []
    no_app = []
    for uni in unis:
        admission_students = Student_details.query.filter_by(selected_uni_id = uni.id).all()
        admissions = []
        admission_ids = []
        for student in admission_students:
            admissions.append({
                'details': student, 
                'application': Application.query.filter_by(id = student.selected_app_id).first(),
                'user': User.query.filter_by(id = student.user_id).first()
            })
            admission_ids.append(student.id)

        others=[]
        for application in Application.query.filter_by(uni_id = uni.id).all():
            if application.student_id not in admission_ids:
                student = Student_details.query.filter_by(id = application.student_id).first()
                others.append({
                    'details': student,
                    'application': application,
                    'user': User.query.filter_by(id = student.user_id).first()
                })
        no_add.append(len(admission_ids))
        no_app.append(len(others))
    
    return no_add, no_app

def sort_by_similarity(arr, string, column):
    similarities=[]
    for item in arr:
        similarities.append([item, similarity_of_2_strings(str(getattr(item, column)), string)])
    similarities = sorted(similarities, key=lambda x: x[1])
    
    output = []
    for item in similarities:
        output.append(item[0])
    return output

def similarity_of_2_strings(string1, string2):
    # Get the lengths of the input strings
    m = len(string1)
    n = len(string2)
 
    # Initialize two rows for dynamic programming
    prev_row = [j for j in range(n + 1)]
    curr_row = [0] * (n + 1)
 
    # Dynamic programming to fill the matrix
    for i in range(1, m + 1):
        # Initialize the first element of the current row
        curr_row[0] = i
 
        for j in range(1, n + 1):
            if string1[i - 1] == string2[j - 1]:
                # Characters match, no operation needed
                curr_row[j] = prev_row[j - 1]
            else:
                # Choose the minimum cost operation
                curr_row[j] = 1 + min(
                    curr_row[j - 1],  # Insert
                    prev_row[j],      # Remove
                    prev_row[j - 1]    # Replace
                )
 
        # Update the previous row with the current row
        prev_row = curr_row.copy()
 
    # The final element in the last row contains the Levenshtein distance
    return curr_row[n]