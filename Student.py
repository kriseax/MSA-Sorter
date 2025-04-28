class Student:
    #major_selections = []
    #minor_selections = []
    def __init__(self, first_name, last_name, school, email, gender, preferred_name, DOB, major_selections, minor_selections):
        self.first_name = first_name
        self.last_name = last_name
        self.school = school
        self.email = email
        self.gender = gender
        self.preferred_name = preferred_name
        self.DOB = DOB
        self.major_selections = major_selections #rank: class
        self.minor_selections = minor_selections #rank: class
        self.assigned_major = ""
        self.assigned_minor = ""

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_class_rank(self, the_class):
        for choice, class_title in self.major_selections.items():
            
            if (the_class == class_title):
                return choice
        
        return -1
    
    def get_class_choice_rank(self):
        return self.get_class_rank(self.assigned_major)
    
    def get_minor_class_rank(self, the_class):
        for choice, class_title in self.minor_selections.items():
            
            if (the_class == class_title):
                return choice
        
        return -1
        
    def get_minor_class_rank_choice(self):
        return self.get_minor_class_rank(self.assigned_minor)
    
    def write_record(self):
        major = self.assigned_major.replace(",", ";")
        minor = self.assigned_minor.replace(",", ";")
        return f"{self.first_name},{self.preferred_name},{self.last_name},{self.DOB},{self.email},{self.school},{major},{minor}\n"
        