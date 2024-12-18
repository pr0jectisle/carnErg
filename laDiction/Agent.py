import math

class Agent:
    def __init__(self):
        self.reward_points = 0
        self.lastReward = 0
        self.tolerance = 0
        self.dependence = 0
        self.craving = 0
        self.initialReward = 5
        self.status = "Neutral "
        self.recovery = 0
        self.flag = False

    def act(self, num=1):
        reward = max(num , num*(self.initialReward - self.tolerance + self.craving))
        #Relapse :
        
        reward += self.recovery
        self.reward_points += reward
        self.dependence += num
        self.tolerance += num/2
        self.craving = 0
        self.recovery = 0
        print(f"Dose taken, dependence: {(self.dependence)}, craving: {(self.craving)}, tolerance: {(self.tolerance)}, reward: {(reward)}, total rewards: {(self.reward_points)}")
        self.flag = True
        self.lastReward = reward
        self.getStatus()
        

    def dont_act(self):
        #Dont act : If not addicted : reward = 0
        #           If addicted : penalty = grows each time in a row
        penalty = self.craving + 0.5*self.dependence
        self.reward_points -= penalty
        if penalty == 0:
            
            self.recovery += 1
            if self.reward_points > 0:
                self.reward_points -= 0.5*self.recovery
                self.reward_points = max(self.reward_points, 0)
            elif self.reward_points < 0:
                self.reward_points += 0.5*self.recovery
                self.reward_points = min(self.reward_points, 0)
            
        self.craving += self.dependence
        
        print(f"No Dose taken, dependence: {self.dependence}, craving: {(self.craving)}, tolerance: {(self.tolerance)}, penalty: {(penalty)}, total rewards: {(self.reward_points)}")
        if self.dependence == 0:
            if self.craving == 0 and self.reward_points < 0:
                self.reward_points +=  0.5

            self.craving -= 0.5
            self.craving = max(self.craving, 0)
        #Decrease dependence
        self.dependence -= 0.5
        self.dependence = max(self.dependence, 0)
        #Decrease tolerance
        self.tolerance -= 0.5
        self.tolerance = max(self.dependence, 0)
        self.flag = False
        self.lastReward = -penalty
        self.getStatus()
    def compute_high(self):
        bound_last = 0
        if self.lastReward > 0:
            bound_last = min(100, self.lastReward)
        elif self.lastReward < 0:
            bound_last = max(-100,self.lastReward)
        
        bound_total = 0
        if self.reward_points>0:
            bound_total = min(100,self.reward_points)
        elif self.reward_points < 0:
            bound_total = max(-100,self.reward_points)

        #print(self.lastReward)
        #print(bound_total)
        total = 0.5 * bound_last + 0.5 * bound_total
        print(total)

    def getStatus(self):
        addicted = False
        craving = False
        relapse = False
        neutral = False

        if (self.tolerance >= self.initialReward/2) or (self.dependence >= self.initialReward/2):
            addicted = True
        #if last status contained "Craving " && flaf
        if self.craving >= self.initialReward/2:
            craving = True
        if self.status.__contains__("Craving ") and self.flag:
            relapse = True
        if (not (addicted or craving or relapse)):
            neutral = True
        toPrint = ""
        if addicted: 
            toPrint += "Addicted "
        if craving:
            toPrint += "Craving "
        if relapse:
            toPrint += "Relapse "
        if neutral:
            toPrint += "Neutral "
        #print(toPrint)
        self.status = toPrint
        return toPrint
    
    def simulate(self, steps = 50):
        for step in range(steps):
            userInput = str(input(f"Step {step} : are there people in the room ? (y/n)  "))
            if userInput == "y":
                self.act()
            elif userInput == "n" :
                self.dont_act()
            else:
                print("wrong input, try again")
            self.getStatus()

