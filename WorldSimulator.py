from TheWorld import TheWorld
import functools
import matplotlib.pyplot as plt 

QUARANTINE_DAILY_COST  = 3000
HOSPITAL_DAILY_COST    = 20000
TUBE_COST              = 100
MAX_TUBES_PER_TEST     = 20
MIN_DAYS_IN_QUARANTINE = 4

class WorldSimulator:

    def __init__(self):
        self.daily_cost = []
        self.world = TheWorld()
    
    def CheckTubes(self, tubes, day):
        results = []
        tubes_per_id = {}
        for tube in tubes:
            result = 0
            for person_id in tube:
                self.world.population[person_id]["test dates"].append(day)
                
                if tubes_per_id[person_id]:
                    tubes_per_id[person_id] += 1
                    if tubes_per_id[person_id] > MAX_TUBES_PER_TEST:
                        result = 2
                        break
                else:
                    tubes_per_id[person_id] = 1
                if self.world.population[person_id]["sick"]:
                    result = 1
            results.append(result)
        return results
    
    def SendToQuarantine(self, ids_list):
        for person_id in ids_list:
            self.world.population[person_id]["in quarantine"] = True
            self.world.population[person_id]["days in quarantine"] = 0
    
    def RemoveFromQuarantine(self):
        quarantined = self.world.GetQuarantined()
        for person in quarantined:
            person_id = person["id"]
            days_in_quarantine = person["days_in_quarantine"] + 1

            if (days_in_quarantine > MIN_DAYS_IN_QUARANTINE) and (person["cured"] or not person["sick"]):
                self.world.population[person_id]["in quarantine"] = False


    def CalcDailyCost(self, num_of_tubes):
        quarantine_cost = QUARANTINE_DAILY_COST*len(self.world.GetQuarantined())
        hospital_cost = HOSPITAL_DAILY_COST*len(self.world.GetHospitalized())
        tube_cost = TUBE_COST*num_of_tubes
        self.daily_cost.append(quarantine_cost + hospital_cost + tube_cost)

    def StartNewDay(self, day, tubes = [], to_quarantine_list = [], from_quarantine_list = []):
        results = self.CheckTubes(tubes, day)
        self.world.Infect()
        self.world.RemoveCured()
        self.world.Hospitalize()
        self.RemoveFromQuarantine()
        self.SendToQuarantine(to_quarantine_list)
        self.CalcDailyCost(len(tubes or []))
        return results

if __name__ == '__main__':
    sim = WorldSimulator()
    sick_per_day = [len(sim.world.GetNotQuarantined())]
    total_healed = [0]
    for day in range(30):
        sim.StartNewDay(day)
        sick_per_day.append(len(sim.world.GetNotQuarantined()))
        total_healed.append(len(sim.world.GetCured()))
        if not sim.world.GetNotYetSicks():
            break
    
    plt.plot(range(len(sick_per_day)),sick_per_day)
    plt.show()
    plt.plot(range(len(total_healed)),total_healed)
    plt.show()
    plt.plot(range(len(sim.daily_cost)),sim.daily_cost)
    plt.show()
