"""
This is a code to move polygon randomly to new place for Monte Carlo Simulation
"""
import pandas as pd
import numpy as np
import random
import math
import os
import time

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def centeroidnp(arr): #this function define center points of group of points
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return sum_x/length, sum_y/length

def randommove (ori_x, ori_y, center_x, center_y, random_x, random_y):
    #this function move a point to a new place based on centerpoint (old center -> new random center)
    #make sure define the angle for rotation
    trans_x = ori_x - center_x # normalize to zero
    trans_y = ori_y - center_y # normalize to zero
    x_transprime = (math.cos(ang) * trans_x) - (math.sin(ang) * trans_y) # new x coord, from zero
    y_transprime = (math.sin(ang) * trans_x) + (math.cos(ang) * trans_y) # new y coord, from zero
    x_prime = x_transprime + random_x # move to new centroid x
    y_prime = y_transprime + random_y # move to new centroid y  
    return x_prime, y_prime

def insideAOI (point, polygon): #check if a point is inside aera of interest (shapely polygon)
    if polygon.contains(point) is True:
        return True
    if polygon.contains(point) is False:
        return False
    
def randominsideAOI (X_min, X_max, Y_min, Y_max, polygon): 
    #to create a random point that inside the AOI polygon
    while True: 
        try:
            random_x = random.uniform(X_min,X_max)
            random_y = random.uniform(Y_min,Y_max)
            randamcenter = Point (random_x, random_y)
        
            if insideAOI(randamcenter, polygon) is True:
                #print ("Random point inside AOI")
                return random_x, random_y
                break
            else:
                #print (" Random point outside AOI")
                raise Exception
        except:
            print ("outside")
            continue
        
def randomnumber(): #this function randomly pick up # of fire events
    eventnumber = [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 13, 18]
    # this is probability values came from ???
    probability = [0.138888889, 0.055555556, 0.194444444, 0.166666667, 
                   0.055555556, 0.083333333, 0.083333333, 0.083333333, 
                   0.027777778, 0.027777778, 0.027777778, 0.027777778, 0.027777778]
    firenumber = np.random.choice(eventnumber, 1, p = probability)
    return firenumber[0]

        
#set-up aera of interest (AOI)
aoidf = pd.read_csv(r"C:\...\AOI_point.txt") #<----- A file giving the AOI polygon

#define AOI polygon, the coordinate system is ??? 
X_min = 532378.004700
X_max = 780094.157044
Y_min = 4246419.794000
Y_max = 4654286.669000
aoiarr = aoidf[['POINT_X', 'POINT_Y']].to_numpy()
polygon = Polygon(aoiarr)

#set_up study area (SA) polygon. The study area is inside the AOI
SAdf = pd.read_csv(r"C:\...\SA_point.txt") #<----- A file giving the SA polygon
SAarr = SAdf[['POINT_X', 'POINT_Y']].to_numpy()
SApolygon = Polygon(SAarr)

#loading list of event
listdf = pd.read_csv(r"C:\...\list_events_after2000.txt") #<----- This is a file giving all the event information
eventlist = listdf['fire1984_6'].tolist()

# ------------------ START SIMULATION HERE -----------------------

for simulation in range (1, 100): #here you define the simulation number start / end 
    start_time = time.time()
    print (" #########   start simulation# ", simulation +1) 
    
    for year in range (100): #here you define how many years for 1 simulation, 100 time is apply here
        
        num_fire = randomnumber() #random select from previous # of events
        
        if num_fire > 0:
            selectevent = random.sample(eventlist, num_fire)
            print ("***** start with year ", year + 1, 'select ', num_fire, " fires *****")
            print (selectevent)
        
            #set up environment for random move
            folderpath = r"C:\...\event_txt_file" #<----- Set a path for file saving
            directory = os.fsencode(folderpath)
            
            #move events
            for event in selectevent:
                print ("-----> now processing: ", event)

                for file in os.listdir(directory): #compile event dataframe
                    filename = os.fsdecode(file)
                    
                    if filename[11:11+len(event)] == event: #double check this! might have same name because of the fire event names!!
                        print (filename)
                        
                        # This is extract step to deal with complicated polygons.
                        if filename.endswith("no_hole.txt"):
                            noholedf = pd.read_csv(folderpath+"\\"+ filename, delim_whitespace=True)
                            noholedf['type'] = 'no_hole'
                        if filename.endswith("donut.txt"):
                            donutdf = pd.read_csv(folderpath+"\\"+ filename, delim_whitespace=True)
                            donutdf['type'] = 'donut'
                        if filename.endswith("hole_hole.txt"):
                            holeholedf = pd.read_csv(folderpath+"\\"+ filename, delim_whitespace=True)
                            holeholedf['type'] = 'hole_hole'
                        if filename.endswith("extra.txt"):
                            extradf = pd.read_csv(folderpath+"\\"+ filename, delim_whitespace=True)
                            extradf['type'] = 'extra'
            
                frame = [noholedf,donutdf,holeholedf,extradf]        
                combinedf = pd.concat(frame)
                combinedf.insert(0, 'UID', range(0, 0 + len(combinedf))) #keep exactly order
         
                xyarr = combinedf[['POINT_X', 'POINT_Y']].to_numpy()
                ptcenter = centeroidnp(xyarr)

                movedarray = []
                ang = random.random() * 2 * math.pi # here you generate a random angle for moved event

                while True: #create random moved point inside AOI
                    try:
                        rnd_x, rnd_y = randominsideAOI(X_min, X_max, Y_min, Y_max, polygon)
                        for x, y in xyarr:
                            movedpoint = randommove (x, y, ptcenter[0], ptcenter[1], rnd_x, rnd_y)
                            newmove = Point (movedpoint)
                
                            if insideAOI(newmove, polygon) is True:
                                movedarray.append ((x, y, movedpoint[0], movedpoint[1]))
                                continue
                            else:
                                movedarray.clear()
                                raise Exception
                        break
    
                    except:
                        print ("...movedpoint not inside")
                        continue
    
                moveddf = pd.DataFrame(movedarray, columns =['ori_x', 'ori_y', 'new_x', 'new_y'])
                
                finalcombine = pd.merge(combinedf, moveddf, how='inner', left_on=['POINT_X', 'POINT_Y'], right_on = ['ori_x', 'ori_y'])
                finalcombine.sort_values(by=['UID'], inplace=True)
                final2 = finalcombine.drop_duplicates(subset=['UID'])
    
                final2.to_csv(r"C:\..." + "\\" + event + "_s" + str(simulation + 1) + "_y" + str(year + 1) + ".txt") #<----- Here ginving the path to save file
                
                checkarray = moveddf[['new_x', 'new_y']].to_numpy()

                # This step filter polygons to maker sure it is inside the SA
                for x, y in checkarray:
                    checkpoint = Point (x, y)
                    if insideAOI(checkpoint, SApolygon) is True:
                        print ("!!! moved event inside SA, export to a txt file !!!")
                        final2.to_csv(r"C:\..." + "\\" + event + "_s" + str(simulation + 1) + "_y" + str(year + 1) + ".txt") #<----- Here ginving the path to save file
                        break
                    else:
                        continue
                
            #print ("finshed processing year: ", year +1)

    print("--- %.2f seconds --- " %(time.time() - start_time)) #here tell you how long it takes for 1 simulation
                        
                
    
           
