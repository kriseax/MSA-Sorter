import pandas as pd
import numpy as np
from Major import Major
from Minor import Minor
from Student import Student
from HouseSort import HouseSort
import random
import os


#Deifine Constant Variables
CATEGORY_DICT = category_dict = {
        "1": "Math/Comp Sci",
        "2": "Science",
        "3": "History",
        "4": "Writing/Lit",
        "5": "Behavioral/Social Science",
        "6": "Not Books"
    }

#2024 begin 10
BEGIN_MAJOR = 9 
END_MAJOR = 30
BEGIN_MINOR = 31
END_MINOR = 49

def main():
    student_list = []
    students_who_need_to_select_major_minor = []
    #read data file into a dataframe
    df = pd.read_csv('scholar_data_2025.csv')

    #drop rows if all null values - to clean up data
    df.dropna(how='all', inplace=True)

    #create dictionary of majors an minors
    #get the column names
    columns = df.columns.to_list()
    majors, minors = get_majors_minors(columns)

    #Create list of student objects
    for index, row in df.iterrows():
        student_major_choices, student_minor_choices = get_student_major_minor_choices(row, majors, minors)
        
        # if major and minor choices are empty do not place studebt in list
        if (len(student_major_choices) != 4 or len(student_minor_choices) != 4):
            students_who_need_to_select_major_minor.append(Student(row['First Name'], row['Last Name'], row['School'].strip(), row['e-mail address'], row['Gender'], row['Preferred First Name'], row['DOB'], student_major_choices, student_minor_choices))
            continue

        student_list.append(Student(row['First Name'], row['Last Name'], row['School'].strip(), row['e-mail address'], row['Gender'], row['Preferred First Name'], row['DOB'], student_major_choices, student_minor_choices))
    
    #create a file with the names of scholars who did not select majors and/or minors
    log_scholars_to_contact(students_who_need_to_select_major_minor)

    #randomly shuffle student list
    random.shuffle(student_list)

    #assign students to majors and minors randomly
    first_pass_assign_major(student_list, majors)

    #write a log
    write_csv_file(majors, "major_log_v1.csv", "major")

    #do a second pass to more evenly and fairly distribute the classes
    second_pass_assign_major(student_list, majors)

    #write a log
    write_csv_file(majors, "major_assigned_final.csv", "major")

    #assign minors
    #Reverse ----sort student list based on the major they were assigned
    student_list = sorted(student_list, key=lambda student: student.get_class_choice_rank(), reverse=True)

    #Assign students to minors
    first_pass_assign_minor(student_list, minors, majors)

    #write a log
    write_csv_file(minors, "minor_log_v1.csv", "minor")

    second_pass_assign_minor(student_list, minors, majors)

    #write a log
    write_csv_file(minors, "minor_log_v2.csv", "minor")

    second_pass_assign_minor(student_list, minors, majors)

    #write a log
    write_csv_file(minors, "minor_assigned_final.csv", "minor")

    #write one spreadsheet
    write_student_data(student_list)

    boomba()

    #get male and female students seperately
    male_list = get_scholar_by_gender(student_list, "Male")
    female_list = get_scholar_by_gender(student_list, "Female")

    #sort the houses
    house_sorter = HouseSort()
    
    house_sorter.house_scholars(female_list, "Female")
    house_sorter.house_scholars(male_list, "Male")
    #house_sorter.print_houses()
    
    input()
    return

#Function to write all student data to a file
def write_student_data(student_list):

    student_list = sorted(student_list, key=lambda x: x.last_name)
    
    with(open("OneSpreadsheet.csv", "w")) as file:
        file.write(f"First Name,Preferred Name,Last Name,DOB,email address,School,Major,Minor\n")
        for student in student_list:
            file.write(student.write_record())
    
    return

#Function to assign students 
def second_pass_assign_major(student_list, class_dict):
    #sort class list from lowest enrollment to highest enrollment
    class_dict = dict(sorted(class_dict.items(), key=lambda x: x[1].get_current_enrollment()))
    
    #make a list of students who were assigned to classes they did not choose
    students_who_did_not_choose = []
    #find all students who chose the low enrollemnt class, order list by the rank they chose, search for 2, 3, 4 choice students and
    for student in student_list:
        if(student.get_class_choice_rank() == -1):
            students_who_did_not_choose.append(student) 

    #remove students who did not choose their assigned major from their currently assigned major
    for student in students_who_did_not_choose:
        class_dict[student.assigned_major].remove_student_from_course(student)
        student.assigned_major = ""

    #sort class list from lowest enrollment to highest enrollment
    class_dict = dict(sorted(class_dict.items(), key=lambda x: x[1].get_current_enrollment()))
    
    #move student from a high enrollment class to low enrollment class
    for course_title, course in class_dict.items():
        #get list of students who chose the class
        students_who_chose_course = get_students_who_chose_course(student_list, course_title, students_who_did_not_choose)
        #Move students into the course from higher enrollment courses
        move_student_from_high_to_low_enrollment(students_who_chose_course, course_title, class_dict)
        
    #place students who were initially placed in classes they did not choose into a class now
    for student in students_who_did_not_choose:
        student_enrolled = False
        for choice, course in student.major_selections.items():
            #if there is room to enroll in course and doesnt have another student from the school the enroll the student
            if (class_dict[course].can_enroll_student() and not class_dict[course].has_student_from_school(student.school)):
                class_dict[course].add_student_to_course(student)
                student.assigned_major = course
                student_enrolled = True
                print(f"Added {student.get_full_name()} to {course}")
                break
        
        #randomly assign student if needed. If they were unable to be enrolled in a major
        if(not student_enrolled):
            random_selection = random.randint(1, 4)
            class_dict[student.major_selections[random_selection]].add_student_to_course(student)
            student.assigned_major = class_dict[student.major_selections[random_selection]].title
            print(f"Randomly Added {student.get_full_name()} to {student.major_selections[random_selection]}")
    
    return

#Function to assign students 
def second_pass_assign_minor(student_list, class_dict, major_dict):
    #sort class list from lowest enrollment to highest enrollment
    class_dict = dict(sorted(class_dict.items(), key=lambda x: x[1].get_current_enrollment()))
    
    #make a list of students who were assigned to classes they did not choose
    students_who_did_not_choose = []
    #find all students who chose the low enrollemnt class, order list by the rank they chose, search for 2, 3, 4 choice students and
    for student in student_list:
        if(student.get_minor_class_rank_choice() == -1):
            students_who_did_not_choose.append(student) 

    #remove students who did not choose their assigned minor from their currently assigned minor
    for student in students_who_did_not_choose:
        class_dict[student.assigned_minor].remove_student_from_course(student)
        student.assigned_minor = ""

    #sort class list from lowest enrollment to highest enrollment
    class_dict = dict(sorted(class_dict.items(), key=lambda x: x[1].get_current_enrollment()))
    
    #move student from a high enrollment class to low enrollment class
    for course_title, course in class_dict.items():
        #get list of students who chose the class
        students_who_chose_course = get_students_who_chose_minor_course(student_list, course_title, students_who_did_not_choose)
        #Move students into the course from higher enrollment courses
        move_student_from_high_to_low_enrollment_minor(students_who_chose_course, course_title, class_dict, major_dict)
        
    #place students who were initially placed in classes they did not choose into a class now
    for student in students_who_did_not_choose:
        student_enrolled = False
        for choice, course in student.minor_selections.items():
            #if there is room to enroll in course and doesnt have another student from the school the enroll the student
            if (class_dict[course].can_enroll_student() and not class_dict[course].has_student_from_school(student.school) and (class_dict[course].teacher != major_dict[student.assigned_major].teacher) and (class_dict[course].category != major_dict[student.assigned_major].category)):
                class_dict[course].add_student_to_course(student)
                student.assigned_minor = course
                student_enrolled = True
                print(f"Added {student.get_full_name()} to {course}")
                break
        
        #randomly assign student if needed. If they were unable to be enrolled in a minor
        if(not student_enrolled):
            random_selection = random.randint(1, 4)
            class_dict[student.minor_selections[random_selection]].add_student_to_course(student)
            student.assigned_minor = class_dict[student.minor_selections[random_selection]].title
            print(f"Randomly Added {student.get_full_name()} to {student.minor_selections[random_selection]}")
    
    return

#Function to move a student from a high enrollment class to a low enrollment class 
def move_student_from_high_to_low_enrollment(students_who_chose_course, course_title, class_dict):
    
    for student in students_who_chose_course:
        if (class_dict[student.assigned_major].get_current_enrollment() >= 16 and not class_dict[course_title].has_student_from_school(student.school) and class_dict[course_title].get_current_enrollment() < 17):
            #place student in course and remove from old course. update asigned major
            class_dict[student.assigned_major].remove_student_from_course(student)
            class_dict[course_title].add_student_to_course(student)
            student.assigned_major = course_title
        
        if (class_dict[course_title].get_current_enrollment() >= 16):
            break
    
    return

#Function to move a student from a high enrollment Minor class to a low enrollment Minor class 
def move_student_from_high_to_low_enrollment_minor(students_who_chose_course, course_title, class_dict, major_dict):
    
    for student in students_who_chose_course:
        if (class_dict[student.assigned_minor].get_current_enrollment() >= 16 and not class_dict[course_title].has_student_from_school(student.school)) and (class_dict[course_title].get_current_enrollment() < 16) and (class_dict[course_title].teacher != major_dict[student.assigned_major].teacher):
            #place student in course and remove from old course. update asigned major
            class_dict[student.assigned_minor].remove_student_from_course(student)
            class_dict[course_title].add_student_to_course(student)
            student.assigned_minor = course_title
        
        if (class_dict[course_title].get_current_enrollment() >= 16):
            break
    
    return
        

#Function to return a list of students who chose a particular Major course
def get_students_who_chose_course(student_list, course_title, students_who_did_not_choose):
    students_who_chose_course = []
    for student in student_list:
        if(student.get_class_rank(course_title) != -1 and student.assigned_major != course_title and student not in students_who_did_not_choose):
            students_who_chose_course.append(student)

    students_who_chose_course = sorted(students_who_chose_course, key=lambda student: student.get_class_rank(course_title))
    
    return students_who_chose_course

#Function to return a list of students who chose a particular Minor course
def get_students_who_chose_minor_course(student_list, course_title, students_who_did_not_choose):
    students_who_chose_course = []
    for student in student_list:
        if(student.get_minor_class_rank(course_title) != -1 and student.assigned_minor != course_title and student not in students_who_did_not_choose):
            students_who_chose_course.append(student)

    students_who_chose_course = sorted(students_who_chose_course, key=lambda student: student.get_class_rank(course_title))
    
    return students_who_chose_course

#Function to write csv file
def write_csv_file(classes_list, file_name, track):
    log_path = "logs" 
    path_exists = os.path.exists(log_path)
    if(not path_exists):
        os.makedirs(log_path)

    csv_file = open(log_path +'/'+file_name, 'w')
    if track == "major":
        csv_file.write("Full Name,School,Gender,Assigned Major,Chosen Rank\n")
    else:
        csv_file.write("Full Name,School,Gender,Assigned Minor,Chosen Rank\n")
    
    for the_class in classes_list.values():
        csv_file.write('\n\n' + the_class.title + '\n')
        for student in the_class.list_of_students:
            #get the class rank for the student
            if track == "major":
                try:
                    rank_key = list(filter(lambda x: student.major_selections[x] == the_class.title, student.major_selections))[0]
                except:
                    rank_key = -1
                major = student.assigned_major.replace(",", ";")
                csv_file.write(f"{student.get_full_name()},{student.school},{student.gender},{major},{rank_key}\n")
            else:
                try:
                    rank_key = list(filter(lambda x: student.minor_selections[x] == the_class.title, student.minor_selections))[0]
                except:
                    rank_key = -1
                minor = student.assigned_minor.replace(",", ";")
                csv_file.write(f"{student.get_full_name()},{student.school},{student.gender},{minor},{rank_key}\n")
    
    csv_file.close()
    return

#Function to assign students a major: First pass
def first_pass_assign_major(student_list, majors_dict):
    not_assigned_list = []
    for student in student_list:
        #calculate weight for top 4 choices
        #create a dictionary of weights and selections
        weight_dict = {}
        for rank_choice in student.major_selections.keys():
            #place student in class choice with the lowest rank
            #get class capacity. if capacity = 0, assign a very small number
            capacity = majors_dict[student.major_selections[rank_choice]].get_percent_enrolled()
            if capacity == 0:
                capacity = 0.001
            #get number of students from the same school
            num_students = get_common_school_students(student, majors_dict[student.major_selections[rank_choice]]) 
            if num_students == 0:
                num_students = 0.001
            weight = (0.5 * rank_choice) * (0.2 * capacity) * (0.3 * num_students)
            weight_dict[rank_choice] = weight
    
        #assign the student a class based on the weight
        #sort weight dictionary by value in ascending order
        weight_dict = dict(sorted(weight_dict.items(), key=lambda x:x[1]))

        student_assigned = False
        #do not assign students to class if teacher from same school or class is full
        for rank in weight_dict.keys():
            course = student.major_selections[rank]
            if student.school != majors_dict[course].teacher_school and not majors_dict[student.major_selections[rank]].class_full():
                majors_dict[student.major_selections[rank]].add_student_to_course(student)
                student.assigned_major = course
                student_assigned = True
                break
        
        #if student not assigned to a class in their selection attempt to enroll in a class in their category
        if not student_assigned:
            #log the student
            not_assigned_list.append(student)
            second_attempt_class_assign(student, majors_dict)
    
    #write log
    log_file = open("first_pass_unassigned.txt", 'w')
    for student in not_assigned_list:
        log_file.write(f"{student.get_full_name()}\n")

    log_file.close()

    return

#Function to assign a student who whas not enrolled on the first pass to assign a major
def second_attempt_class_assign(student, class_dict):

    student_assigned = False
    for course in student.major_selections.values():
        #get course category
        category = class_dict[course].category 
        
        #assign course from category
        for the_class in class_dict.values():
            if the_class.category == category and not the_class.class_full():
                the_class.add_student_to_course(student)
                student.assigned_major = the_class.title
                student_assigned = True
                break
        
        if student_assigned:
            break

    #randomly assign student to a major they werent able to be assigned yet
    if (not student_assigned):
        print(student.get_full_name())
        choice = random.randint(1, 4)
        class_dict[student.major_selections[choice]].add_student_to_course(student)
        student.assigned_major = student.major_selections[choice]


    return

#Function to assign students a major: First pass
def first_pass_assign_minor(student_list, minors_dict, majors_dict):
    not_assigned_list = []
    for student in student_list:
        #calculate weight for top 4 choices
        #create a dictionary of weights and selections
        weight_dict = {}
        for rank_choice in student.minor_selections.keys():
            #place student in class choice with the lowest rank
            #get class capacity. if capacity = 0, assign a very small number
            capacity = minors_dict[student.minor_selections[rank_choice]].get_percent_enrolled()
            if capacity == 0:
                capacity = 0.001
            #get number of students from the same school
            num_students = get_common_school_students(student, minors_dict[student.minor_selections[rank_choice]]) 
            if num_students == 0:
                num_students = 0.001
            weight = (0.5 * rank_choice) * (0.2 * capacity) * (0.3 * num_students)
            weight_dict[rank_choice] = weight
    
        #assign the student a minor class based on the weight
        #sort weight dictionary by value in ascending order
        weight_dict = dict(sorted(weight_dict.items(), key=lambda x:x[1]))

        student_assigned = False
        #do not assign students to class if teacher from same school or class is full, or same major teacher, or same category as major
        for rank in weight_dict.keys():
            course = student.minor_selections[rank]
            if (student.school != minors_dict[course].teacher_school and not minors_dict[student.minor_selections[rank]].class_full()) and (minors_dict[student.minor_selections[rank]].teacher != majors_dict[student.assigned_major].teacher) and (minors_dict[student.minor_selections[rank]].category != majors_dict[student.assigned_major].category):
                
                minors_dict[student.minor_selections[rank]].add_student_to_course(student)
                if course == "Breakout!":
                    print(f"Enrollment: {minors_dict['Breakout!'].currently_enrollment} --- Class Full: {minors_dict['Breakout!'].class_full()}")
                    print(f"Student Added: {student.get_full_name()}\n")

                student.assigned_minor = course
                student_assigned = True
                break
        
        #if student not assigned to a class in their selection attempt to enroll in a class in their category
        if not student_assigned:
            #log the student
            not_assigned_list.append(student)
            second_attempt_minor_class_assign(student, minors_dict, majors_dict)
    
    #write log
    log_file = open("first_pass_unassigned_minor.txt", 'w')
    for student in not_assigned_list:
        log_file.write(f"{student.get_full_name()}\n")

    log_file.close()

    return

#Function to assign a student who whas not enrolled on the first pass to assign a major
def second_attempt_minor_class_assign(student, class_dict, majors_dict):
    student_assigned = False
    for course in student.minor_selections.values():
        #get course category
        category = class_dict[course].category 
        student_assigned = False
        #assign course from category
        for the_class in class_dict.values():
            if the_class.category == category and not the_class.class_full() and student.school != class_dict[course].teacher_school and (class_dict[course].teacher != majors_dict[student.assigned_major].teacher) and (class_dict[course].category != majors_dict[student.assigned_major].category):
                the_class.add_student_to_course(student)
                student.assigned_minor = the_class.title
                student_assigned = True
                break
        
        if student_assigned:
            break
    
    if not student_assigned:
        print(student.get_full_name())
        random_selection = random.randint(1, 4)
        #remove later
        if student.first_name == "Zeke":
            random_selection = random.randint(1, 3)

        class_dict[student.minor_selections[random_selection]].add_student_to_course(student)
        student.assigned_minor = class_dict[student.minor_selections[random_selection]].title

    return

#Function to get number of students from a common school
def get_common_school_students(the_student, course):
    #get count of students in the same school
    number_of_students = 0
    for student in course.list_of_students:
        if (the_student.school == student.school):
            number_of_students += 1
    
    return number_of_students    
    

#Function to get the student major and minor choices    
def get_student_major_minor_choices(df_row, major_dict, minor_dict):
    major_choices = {}
    minor_choices = {}
    counter = -1
    for column, value in df_row.items():
        counter += 1
        if(counter < BEGIN_MAJOR or counter > END_MINOR):
            continue
        #get course name
        course, _, _, _ = get_course_and_teacher(column)
        if(course in major_dict.keys() and value > 0):
            major_choices[int(value)] = course
        elif(course in minor_dict.keys() and value > 0):
            minor_choices[int(value)] = course
    
    #sort based on rank
    major_choices = dict(sorted(major_choices.items(), key=lambda x:x[0]))
    minor_choices = dict(sorted(minor_choices.items(), key=lambda x:x[0]))
    return major_choices, minor_choices

#Function to create a dictionary of majors and minors: key -> title, value -> course object
def get_majors_minors(column_names):
    majors = {}
    minors = {}
    for index in range(len(column_names)):
        #get majors
        if (BEGIN_MAJOR <= index <= END_MAJOR):
            #get class title and instructor
            course, teacher, school, category = get_course_and_teacher(column_names[index])
            majors[course] = Major(course, teacher, school, category)
        if (BEGIN_MINOR <= index <= END_MINOR):
            #get class title and instructor
            course, teacher, school, category = get_course_and_teacher(column_names[index])
            minors[course] = Minor(course, teacher, school, category)

    return majors, minors

#Function to get the course and teacher
def get_course_and_teacher(column_string):

    values = column_string.split("--")
    course = values[0]
    teacher = values[1]
    school = values[2]

    category = CATEGORY_DICT[values[3]]
    return course, teacher, school, category

def get_scholar_by_gender(student_list, gender):
    gendered_list = []
    for scholar in student_list:
        if scholar.gender == gender:
            gendered_list.append(scholar)
    
    return gendered_list

def log_scholars_to_contact(student_list):
    #write log
    file_name = "contact_scholars_major_minor.txt"
    log_path = "logs"
    file_write_path = os.path.join(log_path, file_name)
    
    log_file = open(file_write_path, 'w')
    log_file.write(f"Contact these scholars because they did not select majors and/or minors.\n\nContact Scholars\n-------------------\n")
    log_file.write(f"Claire Lucas\n") #remove this in 2026
    for student in student_list:
        log_file.write(f"{student.get_full_name()}\n")

    log_file.close()


def boomba():
    output = """   




    
    
 ____   ___   ___  __   __ ____   ___  _ _ _ 
|  _ \ / _ \ / _ \|  \ /  |  _ \ / _ \| | | |
| |_) ) | | | | | |   v   | |_) ) |_| | | | |
|  _ (| | | | | | | |\_/| |  _ (|  _  |_|_|_|
| |_) ) |_| | |_| | |   | | |_) ) | | |_ _ _ 
|____/ \___/ \___/|_|   |_|____/|_| |_(_|_|_)                                                                                                                                                                                                                          
    """
    print(output)

    print("\nPress any key to end the program!!!!")


main()
