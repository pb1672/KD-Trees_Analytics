import sys
import time
import csv
from decimal import Decimal
import numpy as np
from scipy.spatial import KDTree
from collections import Counter
#from geopandas import *
import matplotlib.pyplot as plt

import shapefile, sys
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.ticker import MaxNLocator
import pyproj

#Decimal(str(16.2)).quantize(Decimal('.01'), rounding=ROUND_UP)
def dist(p1, p2, p3, p4):
    return ((p1-p3)**2 + (p2-p4)**2)**(0.5)

def loadRoadNetworkIntersections(filename):
    #bbox around Manhattan
    latBounds = [40.6,40.9]
    lngBounds = [-74.05,-73.90]
    #
    listWithIntersectionCoordinates = []
    f = open(filename)
    reader = csv.reader(f, delimiter=' ')
    for l in reader:
        try:
            point = [float(l[0]),float(l[1])]
            if latBounds[0] <= point[0] <= latBounds[1] and lngBounds[0] <= point[1] <= lngBounds[1]:
                listWithIntersectionCoordinates.append(point)
        except:
            print l

    return listWithIntersectionCoordinates

def loadTaxiTrips(filename):
    #load pickup positions
    loadPickup = True
    #bbox around Manhattan
    latBounds = [40.6,40.9]
    lngBounds = [-74.05,-73.90]
    #
    f = open(filename)
    reader = csv.reader(f)
    header = reader.next()
    #
    if loadPickup:        
        lngIndex = header.index(' pickup_longitude')
        latIndex = header.index(' pickup_latitude')
    else:
        latIndex = header.index(' dropoff_latitude')
        lngIndex = header.index(' dropoff_longitude')
    result = []
    for l in reader:
        try:
            point = [float(l[latIndex]),float(l[lngIndex])]
            if latBounds[0] <= point[0] <= latBounds[1] and lngBounds[0] <= point[1] <= lngBounds[1]:
                result.append(point)

        except:
            print l
    return result
    
def naiveApproach(intersections, tripLocations):

    counts = {}
    startTime = time.time()

    minimum = 1000000000

    for a in tripLocations:
        
        for b in intersections:
            
            flag = dist(a[0],a[1],b[0],b[1])
            if minimum > flag:
                minimum = flag
                x=b[0]
                y=b[1]
        counter = counts.setdefault((x,y), 0)
        counts[(x,y)] = counter + 1

    endTime = time.time()
    print 'The naive computation took', (endTime - startTime), 'seconds'
    return counts

def kdtreeApproach(intersections, tripLocations):
    #counts is a dictionary that has as keys the intersection index in the intersections list
    #and as values the number of trips in the tripLocation list which has the key as the closest
    #intersection.
    counts = {}
    startTime = time.time()
    tree = KDTree(intersections)
    points = tree.query(tripLocations,k = 1)
    indexes = points[1]
    counts = Counter(indexes)

    endTime = time.time()
    print 'The kdtree computation took', (endTime - startTime), 'seconds'
    return counts

def plotResults(intersections, counts):
    #TODO: intersect the code to plot here
    proj = pyproj.Proj(init = "esri:26918")
    high = max(counts.values())
    a = set(counts.keys())
    l = set([i for i in xrange(len(intersections))])
    b = list(l - a)
    for x in b:
        counts.setdefault(x, 1)

    for x in counts.keys():
        plt.plot(intersections[x][1], intersections[x][0], 'bo', ms = counts[x]/float(high)*15) #alpha = counts[i]/float(high))

    plt.show()

if __name__ == '__main__':
    #these functions are provided and they already load the data for you
    roadIntersections = loadRoadNetworkIntersections(sys.argv[1])
    tripPickups       = loadTaxiTrips(sys.argv[2])

    
    naiveCounts = naiveApproach(roadIntersections,tripPickups)
    kdtreeCounts = kdtreeApproach(roadIntersections,tripPickups)
    plotResults(roadIntersections,kdtreeCounts)
