from TheWorld import TheWorld
import functools
import matplotlib.pyplot as plt 

QUARANTINE_DAILY_COST  = 3000
HOSPITAL_DAILY_COST    = 20000
TUBE_COST              = 100
MAX_TUBES_PER_TEST     = 20
MIN_DAYS_IN_QUARANTINE = 4

LOW       = 0
HIGH      = 1
FORBIDDEN = 2

 
class WorldSimulator:

    def __init__(self):
        self.daily_cost = []
        self.world = TheWorld()
    
    # Get list of ID's lists and return the results:
    # 0 - No sicks
    # 1 - At least a single sick
    # 2 - If someone's test splitted into more than MAX_TUBES_PER_TEST
    def CheckTubes(self, tubes, day):
        results = []
        tubes_per_id = {}
        for tube in tubes:
            result = 0
            for person_id in tube:
                self.world.population[person_id]["test dates"].append(day)
                
                if person_id in tubes_per_id:
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
    
    # Get ID's and send them to quarantine
    def SendToQuarantine(self, ids_list):
        for person_id in ids_list:
            self.world.population[person_id]["in quarantine"] = True
            self.world.population[person_id]["days in quarantine"] = 0
    
    # Detract people from quarantine
    # Person is get out of quarantine if either he cured
    # or if 4 days of quarantine have passed, the latest.
    def RemoveFromQuarantine(self):
        quarantined = self.world.GetQuarantined()
        for person in quarantined:
            person_id = person["id"]
            days_in_quarantine = person["days in quarantine"] + 1

            if (days_in_quarantine > MIN_DAYS_IN_QUARANTINE) and (person["cured"] or not person["sick"]):
                self.world.population[person_id]["in quarantine"] = False
                self.world.population[person_id]["out of quarantine"] = True
            else:
                self.world.population[person_id]["days in quarantine"] = days_in_quarantine


    def CalcDailyCost(self, num_of_tubes):
        quarantine_cost = QUARANTINE_DAILY_COST*len(self.world.GetQuarantined())
        hospital_cost = HOSPITAL_DAILY_COST*len(self.world.GetHospitalized())
        tube_cost = TUBE_COST*num_of_tubes
        self.daily_cost.append(quarantine_cost + hospital_cost + tube_cost)

    def StartNewDay(self, day, tubes = [], to_quarantine_list = []):
        results = self.CheckTubes(tubes, day)
        self.world.Infect()
        self.world.RemoveCured()
        self.world.Hospitalize()
        self.RemoveFromQuarantine()
        self.SendToQuarantine(to_quarantine_list)
        self.CalcDailyCost(len(tubes or []))
        return results

    # Return a dictionary depend on the requested verbosity
    # LOW       - Number of: quarantined, out of quarintine and hospitalized 
    # HIGH      - Allowed details of: quarantined, out of quarintine and hospitalized
    # FORBIDDEN - Return full detailes about the pandemic's status 
    def GetStatus(self, verbose=HIGH):
        if verbose == LOW:
            return {
                    "num of people in quarintine"     : len(self.world.GetQuarantined()),
                    "num of people out of quarintine" : len(self.world.GetOutOfQuarantine()),
                    "num of people in hospitalized"   : len(self.world.GetHospitalized())
                   }
        
        if verbose == HIGH:
            return {
                    "In quarintine"     : list(map(self.GetAuthDetailes, self.world.GetQuarantined())),
                    "Out of quarintine" : list(map(self.GetAuthDetailes, self.world.GetOutOfQuarantine())),
                    "Hospitalized"      : list(map(self.GetAuthDetailes, self.world.GetHospitalized())),
                   }

        if verbose == FORBIDDEN:
            return {
                    "In quarintine"     : self.world.GetQuarantined(),
                    "Not in quarintine" : self.world.GetNotQuarantined(),
                    "Out of quarintine" : self.world.GetOutOfQuarantine(),
                    "Hospitalized"      : self.world.GetHospitalized(),
                    "Cured"             : self.world.GetCured(),
                    "Not yet sick"      : self.world.GetNotYetSicks()
                   }

    # Return detail the user id allowed to see
    def GetAuthDetailes(self, person):
        return {
                "id"                : person["id"],
                "related"           : person["related"],
                "in hospital"       : person["in hospital"], 
                "in quarantine"     : person["in quarantine"],
                "out of quarantine" : person["out of quarantine"], 
                "test dates"        : person["test dates"]
               }


if __name__ == '__main__':
    sim = WorldSimulator()
    sick_per_day = [len(sim.world.GetNotQuarantined())]
    total_healed = [0]
    sim.StartNewDay(0, to_quarantine_list = list(range(1000000)))
    for day in range(29):
        sim.StartNewDay(day)
        status = sim.GetStatus(LOW)
        status = sim.GetStatus(HIGH)
        status = sim.GetStatus(FORBIDDEN)
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
