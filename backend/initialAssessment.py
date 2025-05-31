#output list format all of these will be strings
#output format - [KSLOC, cost, predictedTime, budgetC, budgetPC, requiredTeam, Deadline information, Budget information, team changes, productivity, risk%]
#input  format - [teamSize, monthlySalary, budget, deadline, requirements, RS, SD, complexity, experience, PL, ST, DS, number of classes, number of methods]

from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
from datetime import datetime

# csv_path = 'data/Dataset-Normal.csv'
csv_path = 'Dataset-Normal.csv'

#Effor Multipliers
EF = [[0.75, 0.88, 1.00, 1.15, 1.40],#Required software
      [0.94, 0.94, 1.00, 1.08, 1.16],#Size of Database
      [0.70, 0.85, 1.00, 1.15, 1.30],#Complexity of the product
      [1.42, 1.17, 1.00, 0.86, 0.70],#Software engineering capability
      [1.14, 1.07, 1.00, 0.95, 0.88],#Programming language experience
      [1.24, 1.10, 1.00, 0.91, 0.83],#Use of software tools
      [1.23, 1.08, 1.00, 1.04, 1.10]#Required development schedule
      ]

#Project type coefficients
#COEF = [[a,b,c], [a,b,c], [a,b,c]] 
#organic, semi-detached, embedded
COEF = [[2.4, 1.05, 0.38], 
        [3.0, 1.12, 0.35],
        [3.6, 1.20, 0.32],
      ]

def initialAnalysis(input):
      #extract to variables
      teamSize = int(input[0])
      monthlySalary = int(input[1])
      budget = int(input[2])
      effortFactors = [input[5], input[6], input[7], input[8], input[9], input[10], input[11]]
      complexity = int(input[7])
      experience = int(input[8])
      LOCinput = [[int(input[12]), int(input[4]), int(input[13])]]

      #get deadline in months
      current_date = datetime.today()

      # Convert input string to datetime object
      input_date = input[3]
       # always gives the date as DD/MM/YYYY
      input_date = input_date[:10]
      print(input_date)
      input_date = datetime.strptime(input_date, '%Y-%m-%d')

      # Calculate the difference between input date and current date
      delta = (input_date - current_date)
      time = round(delta.days / 30,2)  # assume 30 days per month

      #determine project type
      type = 0
      if (complexity == 5 and complexity > experience) or (teamSize >=28 and not (experience > complexity)) or (teamSize > 40):
            type = 2    #embedded
      elif (teamSize <= 12) and (experience >= complexity):
            type = 0    #organic
      else:
            type = 1    #semi-detached

      a = COEF[type][0]
      b = COEF[type][1]

      # calculate EAF
      # cycle through the effort factors and multiply them together
      EAF = np.prod([EF[i][int(effortFactors[i]) -1] for i in range(len(effortFactors))])

      # read the CSV file into a pandas dataframe
      with open(csv_path, 'r') as f:
            df = pd.read_csv(f)
      y = df.iloc[:, 3].tolist()  # get the results
      X = df.iloc[:, :-1].applymap(int).values.tolist()  # extract rows as a list of integer lists
            
      # Create a linear regression object
      reg = LinearRegression()

      # Train the linear regression model
      reg.fit(X, y)

      #fit linear regression model to code factors inputs
      SLOC = int(reg.predict(LOCinput))
      KSLOC = SLOC / 1000

      # Calculate the size factor
      SF = a * (KSLOC ** b)

      # Calculate the effort and produictivity
      EFFORT = EAF * SF       #effort in person months
      PROD = round(KSLOC / EFFORT,2)      #KSLOC per person per month

      #predicted values
      cost = round(EFFORT * monthlySalary,2) # cost with current team salary and size
      predictedTime = round(EFFORT / teamSize,2) # this value is different to the duration above as it uses the optimal team members number

      providedEffort = teamSize * time #effort months assigned to project

      #now calculations are done round the values to be stored
      KSLOC = round(KSLOC,2)
      MKSLOC = round(KSLOC / time,2)

      #how accurate is the budget against the predictions
      budgetC = round(float(cost) - float(budget),2) #budget change
      budgetPC = round((float(budgetC) / float(budget)) * 100,2) #budget change percentage  

      #how over the deadline are we expected to finish
      timeC = predictedTime - time
      timePC = round((timeC / time) * 100,2)

      #risk percentage factor
      risk = round((budgetPC + timePC) / 2,2)
      #convert to string
      if risk < 0:
            risk = "0%"
      elif risk > 100:
            risk = "100%"
      else:
            risk = str(risk) + "%"

      #List which will be filled with outputs
      outputList = []
      outputList.append(str(KSLOC))
      outputList.append(str(cost))
      outputList.append(str(predictedTime))
      outputList.append(str(budgetC))
      outputList.append(str(budgetPC))

      #set required team size to current team size
      requiredTeam = int(EFFORT / time)
      #to meet deadline the team size may need to be adjusted
      outputList.append(str(requiredTeam))

      #check if the project will meet the deadline
      if EFFORT > providedEffort:
            #the project will not meet the deadline
            outputList.append("With the current setup this project is expected to take: " + str(predictedTime) + " months. This is " + str(round(timeC, 2)) + " months past the deadline!")
      else:
            #the project will meet the deadline
            timeC = abs(timeC)
            outputList.append("With the current setup this project is expected to take: " + str(predictedTime) + " months. This is " + str(round(timeC, 2)) + " months before the deadline!")

      #check id the project is over budget
      if cost > budget:
            outputList.append("WARNING: This project is underfunded. Recommended Budget change: +£" + str(budgetC) + ". This is +" + str(budgetPC) + "%")
      else:
            #do not reccommend a budget change if the PC is <5%
            if budgetPC < 5:
                  outputList.append("This project is on budget.")
            else:
                  outputList.append("WARNING: This project is overfunded. Recommended Budget change: £" + str(budgetC) + ". This is " + str(budgetPC) + "%")
      
      #check the changes in team size
      if requiredTeam > teamSize:
            #team size needs to be increased
            outputList.append("WARNING: There are not enough people assigned to this project! To complete the project in " + str(time) + " months, the team size should be increased to " + str(requiredTeam))
      elif requiredTeam < teamSize:
            #team size could be decreased
            outputList.append("To complete the project in " + str(time) + " months, instead of in " + str(predictedTime) + " months the team size could be decreased to " + str(requiredTeam))

      #productivity
      outputList.append("The productivity required on this project is " + str(MKSLOC) + " thousand lines of code per month")
      
      outputList.append(str(risk))
      return outputList


