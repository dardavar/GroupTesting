from numpy import random
import random as rand
import functools

POPULATION_SIZE   = 100000
INIT_NUM_OF_SICK  = 10
AVG_SICK_DAYS     = 10
DAYS_TO_HOSPITAL  = 7
SEVERE_SICK_PROB  = 0.1
EXPECTED_INFECTED = 1.2
INFECT_PROB       = EXPECTED_INFECTED/POPULATION_SIZE

class TheWorld:

    def __init__(self):
        self.population = []

        for id_num in range(0,POPULATION_SIZE):
            person = {"id": id_num, "sick": False, "cured": False, "in hospital": False, "in quarantine": False, "test dates": []}
            if id_num < 3:
                person["related"] = list(range(id_num+1, id_num+4))
                person["related"].append((id_num - 1) % POPULATION_SIZE)
                person["related"].append((id_num - 2) % POPULATION_SIZE)
                person["related"].append((id_num - 3) % POPULATION_SIZE)
            elif id_num > POPULATION_SIZE - 4:
                person["related"] = []
                person["related"].append((id_num + 1) % POPULATION_SIZE)
                person["related"].append((id_num + 2) % POPULATION_SIZE)
                person["related"].append((id_num + 3) % POPULATION_SIZE)
                person["related"].extend(list(range(id_num-3, id_num)))
            else:
                person["related"] = list(range(id_num+1, id_num+4))
                person["related"].extend(list(range(id_num-3, id_num)))
            self.population.append(person)
        
        self.AddNewSicks(INIT_NUM_OF_SICK, range(POPULATION_SIZE))

    def GetSicks(self):
        return list(filter(lambda x: x["sick"], self.population))

    def GetNotYetSicks(self):
        return list(filter(lambda x: (not x["sick"]) and (not x["cured"]), self.population))

    def GetQuarantined(self):
        return list(filter(lambda x: x["in quarantine"], self.population))

    def GetNotQuarantined(self):
        return list(filter(lambda x: x["sick"] and not x["in quarantine"], self.population))

    def GetHospitalized(self):
        return list(filter(lambda x: x["in hospital"], self.population))
    
    def GetCured(self):
        return list(filter(lambda x: x["cured"], self.population))
    
    def GetTestDates(self):
        return list(map(lambda x: x["test dates"], self.population))
    
    def AddNewSicks(self, numOfInfected, potential_sicks):
        infectedIndex = rand.sample(potential_sicks, numOfInfected)
        
        for index in infectedIndex:
            max_days_of_sickness = random.poisson(AVG_SICK_DAYS)
            while max_days_of_sickness == 0:
                max_days_of_sickness = random.poisson(AVG_SICK_DAYS)
            self.population[index]["max days of sickness"] = max_days_of_sickness
            self.population[index]["days of sickness"] = 0
            self.population[index]["sick"] = True

    def RemoveCured(self):
        sicks = self.GetSicks()

        for sick in sicks:
            sick_id = sick["id"]
            self.population[sick_id]["days of sickness"] += 1
            
            if self.population[sick_id]["days of sickness"] > self.population[sick_id]["max days of sickness"]:
                self.population[sick_id]["sick"] = False
                self.population[sick_id]["cured"] = True
                self.population[sick_id]["in hospital"] = False

    def Infect(self):
        sicks = self.GetSicks()
        potential_sicks = []

        for sick in sicks:
            potential_sicks.extend(sick["related"]) 
        potential_sicks.extend(rand.sample(range(POPULATION_SIZE), len(sicks)))
        potential_sicks = set(potential_sicks)
        potential_sicks = list(potential_sicks & set(map(lambda x: x["id"], self.GetNotYetSicks())))
        
        num_of_new_sicks = min(round(EXPECTED_INFECTED*len(sicks)), len(self.GetNotYetSicks()), len(potential_sicks))
        
        self.AddNewSicks(num_of_new_sicks, potential_sicks)
    
    def Hospitalize(self):
        not_quarantined = self.GetNotQuarantined()
        for person in not_quarantined:
            if person["days of sickness"] == DAYS_TO_HOSPITAL:
                if random.binomial(1,SEVERE_SICK_PROB) == 1:
                    person_id = person["id"]
                    self.population[person_id]["in hospital"] = True