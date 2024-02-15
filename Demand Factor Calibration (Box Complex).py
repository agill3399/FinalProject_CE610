#!/usr/bin/env python
# coding: utf-8

# In[24]:


# This is generic code and has not yet been tested on a system like Martin County. Please adapt where needed and email or call with
# any questions

from epyt import epanet
import numpy as np
import pandas as pd

# Find the file path of the EPANET file in your directory
d = epanet('pathForfile/.inp')

# Read in generic tank data, change the path to match your system
dfTanks = pd.read_excel('C:/Users/apgi227/OneDrive - University of Kentucky/Documents/GitHub/FinalProject_CE610/exampleTankLevels.xlsx')


# create random positive demand factors (here we will create n-1 factors where n is the number of zones in the system)
# This example assumes 4 zones, that is why we are using three factors

demandFactors = [[2, 0.5, 1.4], [4, 1, 1.2], [3, 1.5, 1.1]]


This is where we are storing the solutions for the demand factors
resultPattern1 = [1] * 24
resultPattern2 = [1] * 24
resultPattern3 = [1] * 24
# resultPattern4 = [1] * 24



# the total length of the EPS
for h in range(24):
    
    #tank data for this hour (assuming the excel file has hour 1 in the first column - we do not want hour 0 here)
    # Change depending on the number of tanks to be included within the objective function
    sawmillRoad = dfTanks.iloc[h][1]
    tunnelHill = dfTanks.iloc[h][2]
    colley = dfTanks.iloc[h][3]
    #newTank = dfTanks.iloc[h][nth]
    
    # Change depending on the number of zones in the system. Here we have 4 zones and will therefore be creating (n-1) points
    pointsInSimplex = [1, 1, 1]

    # Change depending on the number of points within the simplex
    while pointsInSimplex[0] >= 0.0000001 or pointsInSimplex[1] >= 0.0000001 or pointsInSimplex[2] >= 0.0000001:

        # change the range to match the number of points in the simplex
        for i in range(3):

            # depending on the number of zones, create demand patterns
            resultPattern1[h] = demandFactors[i][0]
            resultPattern2[h] = demandFactors[i][1]
            resultPattern3[h] = demandFactors[i][2]

        # Here we first discover why we are using (n-1) points in the simplex. Because we want to incorporate real data, we are using
        # a mass balance to determine what the nth demand pattern will be. Add or subrtract patterns to ensure that this suits the system.

            # nthPattern[h] = ((volume in at time t + the change in storage of the tanks(flow out is positive)) - (Base Demand Zone 1 * pattern1) - (Base Demand Zone 2 * pattern2) - (Base Demand zone 3 * pattern3)) / Base Demand nth zone

            # Create appropriate number of demand patterns dependant on system. Make sure this indexes properly within the .inp file.
            # for example d.setPattern(1, [pattern1] + dummyPattern) is calling the first indexed demand pattern in the file and not 
            # necessarily the demand pattern with the name of 1.

            d.setPattern(1, resultPattern1)
            d.setPattern(2, resultPattern2)
            d.setPattern(3, resultPattern3)
            #d.setPattern(nth, resultPattern4)

            d.openHydraulicAnalysis()
            d.initializeHydraulicAnalysis()
            Series = d.getComputedHydraulicTimeSeries()
            d.closeHydraulicAnalysis()

            # Change the below statements (add or subtract) dpending on how many tanks are in your objective function. 
            # You must also go into the .inp file to figure out the exact index of the tanks in the sim (you can use d.getNodeNameID)
            ModelTank1 = Series.Head[2, 306]
            ModelTank2 = Series.Head[2, 307]
            ModelTank3 = Series.Head[2, 304]
            #ModelTank4 = Series.Head[2, 304]

            # Update the objective function to match the number of tanks that are in the simulation. 
            Error = ((ModelTank1 - #realTank1) ** 2) + ((ModelTank2 - #realTank2) ** 2) + ((ModelTank3 - #realTank3) ** 2) + ((ModelTank4 - #realTank4) ** 2)
            pointsInSimplex[i] = Error

        # Change depending on the number of points within the simplex (should equal the number of zones)
        if pointsInSimplex[0] <= 0.0000001 or pointsInSimplex[1] <= 0.0000001 or pointsInSimplex[2] <= 0.0000001:
            
            #if we have reached our condition
            minVal, whereMin = min(pointsInSimplex), pointsInSimplex.index(min(pointsInSimplex))

            #store the calibrated demand factors from this hour
            resultPattern1[h] = demandFactors[whereMin][0]
            resultPattern2[h] = demandFactors[whereMin][1]
            resultPattern3[h] = demandFactors[whereMin][2]
            #nthPattern[h] = ((volume in at time t + the change in storage of the tanks(flow out is positive)) - (Base Demand Zone 1 * pattern1) - (Base Demand Zone 2 * pattern2) - (Base Demand zone 3 * pattern3)) / Base Demand nth zone              
            #advance to next time step h
                      
            break

        else:

            # Change range depending on the number of points in the simplex
            maxVal, whereMax = max(pointsInSimplex), pointsInSimplex.index(max(pointsInSimplex))
            logical = [i for i in range(3) if pointsInSimplex[i] != maxVal]

            ph = demandFactors[whereMax]

            #add another "demandFactors[logical[0,1,2...]][j]" if number of zones change. Also change the denominator as well as the "in range() statement"
            centroid = [(demandFactors[logical[0]][j] + demandFactors[logical[1]][j] + demandFactors[logical[2]][j]) / 3 for j in range(3)]

            # change the range to match the number of points in the simplex
            newPoint = [(2.5 * centroid[j]) - (1.5 * ph[j]) for j in range(3)]

            # Change the "in range()"" statement as well as the size of "newPoint" (create more newPoint values if the number of zones is increased)
            while newPoint[0] < 0 or newPoint[1] < 0 or newPoint[2] < 0:
                newPoint = [(0.5 * newPoint[j]) + (0.5 * centroid[j]) for j in range(3)]

            # change the number of patterns to match the number of zones. If mass balance remove the comment
            resultPattern1[h] = newPoint[0]
            resultPattern2[h] = newPoint[1]
            resultPattern3[h] = newPoint[2]
             # nthPattern[h] = ((volume in at time t + the change in storage of the tanks(flow out is positive)) - (Base Demand Zone 1 * pattern1) - (Base Demand Zone 2 * pattern2) - (Base Demand zone 3 * pattern3)) / Base Demand nth zone

            d.setPattern(1, resultPattern1)
            d.setPattern(2, resultPattern2)
            d.setPattern(3, resultPattern3)
            #d.setPattern(nth, resultPattern4)

            d.openHydraulicAnalysis()
            d.initializeHydraulicAnalysis()

            Series = d.getComputedHydraulicTimeSeries()
            d.closeHydraulicAnalysis()

            #change this to match the tank heads if you change systems
            ModelTank1 = Series.Head[2, 306]
            ModelTank2 = Series.Head[2, 307]
            ModelTank3 = Series.Head[2, 304]
            #ModelTank4 = Series.Head[2, 304]

            Error = ((ModelTank1 - #realTank1) ** 2) + ((ModelTank2 - #realTank2) ** 2) + ((ModelTank3 - #realTank3) ** 2) + ((ModelTank4 - #realTank4) ** 2)

            if Error < maxVal:
                #change is the number of patterns (points in the simplex) increases.
                demandFactors[whereMax] = [pattern1, pattern2, pattern3]
                pointsInSimplex[whereMax] = Error
                print(Error)


            else:

                #change the range() if the number of points in the simplex is increased
                newPoint = [(0.5 * ph[j]) + (0.5 * centroid[j]) for j in range(3)]

                # Evaluate the new point
                # change the number of patterns to match the number of zones. If mass balance remove the comment
                resultPattern1[h] = newPoint[0]
                resultPattern2[h] = newPoint[1]
                resultPattern3[h] = newPoint[2]
                # nthPattern = ((volume in at time t + the change in storage of the tanks(flow out is positive)) - (Base Demand Zone 1 * pattern1) - (Base Demand Zone 2 * pattern2) - (Base Demand zone 3 * pattern3)) / Base Demand nth zone

                d.setPattern(1, resultPattern1)
                d.setPattern(2, resultPattern2)
                d.setPattern(3, resultPattern3)
                #d.setPattern(nth, resultPattern4)

                d.openHydraulicAnalysis()
                d.initializeHydraulicAnalysis()
                Series = d.getComputedHydraulicTimeSeries()
                d.closeHydraulicAnalysis()

                ModelTank1 = Series.Head[2, 306]
                ModelTank2 = Series.Head[2, 307]
                ModelTank3 = Series.Head[2, 304]
                #ModelTank4 = Series.Head[2, 304]

                Error = ((ModelTank1 - #realTank1) ** 2) + ((ModelTank2 - #realTank2) ** 2) + ((ModelTank3 - #realTank3) ** 2) + ((ModelTank4 - #realTank4) ** 2)

                # Change this if the number of patterns (zones) are increased
                demandFactors[whereMax] = [pattern1, pattern2, pattern3]
                pointsInSimplex[whereMax] = Error


            minVal, whereMin = min(pointsInSimplex), pointsInSimplex.index(min(pointsInSimplex))

            #store the calibrated demand factors from this hour
            resultPattern1[h] = demandFactors[whereMin][0]
            resultPattern2[h] = demandFactors[whereMin][1]
            resultPattern3[h] = demandFactors[whereMin][2]
            #nthPattern[h] = ((volume in at time t + the change in storage of the tanks(flow out is positive)) - (Base Demand Zone 1 * pattern1) - (Base Demand Zone 2 * pattern2) - (Base Demand zone 3 * pattern3)) / Base Demand nth zone              
            #advance to next time step h


# In[46]:


#example of bringing in the data frame from an excel file

import pandas as pd
 
# read by default 1st sheet of an excel file
dataframe1 = pd.read_excel('C:/Users/apgi227/OneDrive - University of Kentucky/Documents/GitHub/FinalProject_CE610/exampleTankLevels.xlsx')


# In[48]:


# what the dataframe actually looks like
dataframe1


# In[49]:


# this is how to access its data (using iloc - this indexes the location as [rows][columns])

dataframe1.iloc[0][1]


# In[ ]:




