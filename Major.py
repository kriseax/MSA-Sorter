class Major:

    def __init__(self, title, teacher, teacher_school, category):
        self.title  = title
        self.teacher = teacher
        self.teacher_school = teacher_school
        self.category = category
        self.list_of_students = []
        self.max_students = 20
        self.currently_enrollment = len(self.list_of_students)
        self.percent_enrolled = self.currently_enrollment / self.max_students
    
    def get_current_enrollment(self):
        return len(self.list_of_students)
    
    def add_student_to_course(self, the_student):
        self.list_of_students.append(the_student)
        self.currently_enrollment = len(self.list_of_students)
        return
    
    def remove_student_from_course(self, the_student):
        self.list_of_students.remove(the_student)
        return
    
    def get_percent_enrolled(self):
        return (self.currently_enrollment / self.max_students)
    
    def can_enroll_student(self):
        if(self.get_current_enrollment() < self.max_students):
            return True
        else:
            return False
    
    def class_full(self):
        if self.get_percent_enrolled() >= 1:
            return True
        else:
            return False
        
    def class_student_rank(self):
        total_rank = 0
        for student in self.list_of_students:
            #get the student's class rank
            try:
                rank_key = list(filter(lambda x: student.major_selections[x] == self.title, student.major_selections))[0]
            except:
                rank_key = 5
            total_rank += rank_key
        return total_rank / self.get_current_enrollment()
    
    #Determines if there are students in class who did not choose it
    def has_students_who_did_not_choose(self):
        for student in self.list_of_students:
            #get the student's class rank
            try:
                rank_key = list(filter(lambda x: student.major_selections[x] == self.title, student.major_selections))[0]
            except:
                return True
        
        return False
    
    def has_student_from_school(self, school):
        for student in self.list_of_students:
            if student.school == school:
                return True
        
        return False

