import os
import random
class HouseSort():
    def __init__(self) :

        self.houses = self.load_house_rooms()
        self.male_houses = {
            "213": [], "214": [], "225": [], "313": [], "314": [], "325": [], "413": [], "414": [], "425": []
        }

        self.female_houses = {
            "513": [], "514": [], "525": [], "613": [], "614": [], "625": [], "713": [], "714": [], "725": [], "130": []
        }

        
        self.house_caps = {"725": 16, "714": 16, "614": 16, "613": 16, "514": 16, "513": 16, "425": 16, "414": 16, "313": 16, "314": 16, "213": 16, "214": 16,
                      "713": 18, "413": 18, "625": 20, "525": 20, "325": 20, "225": 20, "130": 24 }
        self.male_house_choices = ["213", "214", "225", "313", "314", "325", "413", "414", "425"]
        self.female_house_choices = ["513", "514", "525", "613", "614", "625", "713", "714", "725", "130"]
        
        self.unassigned_scholars = []
    
    def house_scholars(self, scholar_list, gender):

        self.assign_houses(scholar_list, gender, 0, False)

        counter = 1
        while len(self.unassigned_scholars) > 0:
            self.assign_houses(self.unassigned_scholars, gender, counter, True)
            counter += 1

        #write scholar houses to file
        if gender == "Female":
            self.write_house_to_file(self.female_houses, "female_scholar_houses.csv")
        else:
            self.write_house_to_file(self.male_houses, "male_scholar_houses.csv")

        #assign roommates
        self.assign_roomates("Female")
        self.assign_roomates("Male")

        #assign roommates
        self.write_roommates_to_file("Female", "female_scholar_roommates_houses.csv")
        self.write_roommates_to_file("Male", "male_scholar_roommates_houses.csv")

        #write roommates to a file
        
        return
    
    def assign_roomates(self, gender):

        #set a reference to the dictionary of houses depending on the gender
        gender_house = None
        if gender == "Female":
            gender_house = self.female_houses
        elif gender == "Male":
            gender_house = self.male_houses
        else:
            return

        #loop through the houses one house at a time
        for house in gender_house:
            #loop through the rooms in that house
            for room in self.houses[house]:
                #get two scholars and place in the room
                #loop through the scholars in the house and assign two per room
                while(len(gender_house[house]) > 0):
                    
                    #if 2 or more than scholars left in house assign 2 to the room 
                    if(len(gender_house[house]) >= 2):
                        roomie_1 = gender_house[house][0]
                        roomie_2 = gender_house[house][1]

                        #assign to room
                        self.houses[house][room].append(roomie_1)
                        self.houses[house][room].append(roomie_2)

                        #remove the roomies from the list
                        gender_house[house].remove(roomie_1)
                        gender_house[house].remove(roomie_2)
                        break
                    
                    if(len(gender_house[house]) == 1):
                        roomie_1 = gender_house[house][0]     #get scholar from the list
                        self.houses[house][room].append(roomie_1)   #assign to a room
                        gender_house[house].remove(roomie_1)  #remove the roomies from the list
                        break

        return


    def write_house_to_file(self, house_dict, file_name):
        log_path = "logs" 
        path_exists = os.path.exists(log_path)
        
        if(not path_exists):
            os.makedirs(log_path)
        
        file_write_path = os.path.join(log_path, file_name)

        with(open(file_write_path, "w")) as file:
            file.write(f"First Name,Preferred Name,Last Name,DOB,email address,School,Major,Minor\n")
        
            for house in house_dict:
                file.write(f"House {house} --> House for RA in Room {house}\n")
                for scholar in house_dict[house]:
                    record = scholar.write_record()
                    file.write(record)
                file.write("\n\n")

    def write_roommates_to_file(self, gender, file_name):
        
        #set a reference to the dictionary of houses depending on the gender
        gender_house = None
        if gender == "Female":
            gender_house = self.female_houses
        elif gender == "Male":
            gender_house = self.male_houses
        else:
            return
        
        log_path = "logs" 
        path_exists = os.path.exists(log_path)
        
        if(not path_exists):
            os.makedirs(log_path)
        
        file_write_path = os.path.join(log_path, file_name)

        with(open(file_write_path, "w")) as file:
            file.write(f"First Name,Preferred Name,Last Name,DOB,email address,School,Major,Minor\n")
            for house in gender_house:
                file.write(f"\nHouse {house} --> House for RA in Room {house}\n")
                for room in self.houses[house]:
                    file.write(f"Room {room}: Assigned Scholars\n")
                    for scholar in self.houses[house][room]:
                        file.write(scholar.write_record())
                    file.write("\n")

        return



    #load room dictionary
    def load_house_rooms(self):
        #Create an empty dictionary for the houses
        houses = {}

        #open rooms.csv file
        room_file = open("rooms.csv", "r", encoding='utf-8-sig')

        #loop through the file
        for room_line in room_file:
            rooms = room_line.split(",")

            #set the house as the RA room which is the first in the list
            house = rooms[0]

            #remove the RA room to leave only scholar rooms
            rooms = rooms[1:]
            
            #add house to dictionary the house RA room is the first room in the line of data
            houses[house] = {}
    
            for room in rooms:
                #add room as an empty list
                houses[house][room.strip()] = []

        return houses
    
    def assign_houses(self, scholar_list, gender, threshold, adding_unassigned):
        #loop through list of student
        for scholar in scholar_list:
            placed_in_house = False
            if gender == "Female":
                random.shuffle(self.female_house_choices)
                for house in self.female_house_choices:
                    #check scholar from same school, same major, minor, 
                    if not self.scholar_from_same_school(scholar, self.female_houses[house]) and not \
                    self.scholar_with_same_major(scholar, self.female_houses[house], threshold) and not \
                    self.scholar_with_same_minor(scholar, self.female_houses[house], threshold) and \
                    len(self.female_houses[house]) < self.house_caps[house]:
                        #place scholar in house
                        self.female_houses[house].append(scholar)
                        placed_in_house = True

                        #remove scholar from list if we're adding unassigned scholars
                        if adding_unassigned:
                            scholar_list.remove(scholar)
                        break

                if not placed_in_house and not adding_unassigned:
                    self.unassigned_scholars.append(scholar)

            if gender == "Male":
                random.shuffle(self.male_house_choices)
                for house in self.male_house_choices:
                    #check scholar from same school, same major, minor, 
                    if not self.scholar_from_same_school(scholar, self.male_houses[house]) and not \
                    self.scholar_with_same_major(scholar, self.male_houses[house], threshold) and not \
                    self.scholar_with_same_minor(scholar, self.male_houses[house], threshold) and \
                    len(self.male_houses[house]) < self.house_caps[house]:
                        #place scholar in house
                        self.male_houses[house].append(scholar)
                        placed_in_house = True

                        #remove scholar from list if we're adding unassigned scholars
                        if adding_unassigned:
                            scholar_list.remove(scholar)
                        break

                if not placed_in_house and not adding_unassigned:
                    self.unassigned_scholars.append(scholar)
        
        return

    def scholar_from_same_school(self, scholar, house_list):
        for other_scholar in house_list:
            if scholar.school == other_scholar.school:
                return True
        
        return False
    
    def scholar_with_same_major(self, scholar, house_list, threshold):
        matching_majors = 0

        for other_scholar in house_list:
            if scholar.assigned_major == other_scholar.assigned_major:
               matching_majors += 1
        
        if matching_majors > threshold:
            return True
        else:
            return False
    
    def scholar_with_same_minor(self, scholar, house_list, threshold):
        matching_minors = 0

        for other_scholar in house_list:
            if scholar.assigned_minor == other_scholar.assigned_minor:
               matching_minors += 1
        
        if matching_minors > threshold:
            return True
        else:
            return False

    
    def print_houses(self):
        print(self.houses)

        '''
        for house in self.houses:
            print(f"{house} House")
        '''
