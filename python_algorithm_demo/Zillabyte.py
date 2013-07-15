#!/usr/bin/python
'''
ZILLABYTE ALGORITHM:
  x) deserialize the graph specification from json into a canonical Graph object
  x) use the 'mising arcs can be replaced with the shortest path between two arcs' homomorphism trick to make the incomplete graph a complete graph.
       i. use Floyd-Warshall to calculate these paths:  http://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm
  x) use any TSP heuristic to get a good aproximate solution
       i. I'll use 2-opt to keep it simple:   http://www.dti.unimi.it/~righini/Didattica/Algoritmi%20Euristici/MaterialeAE/Lin%20Kernighan%20TSP.pdf
  x) back out the full path using the Floyd-Warshall 'next' martix and get_path tools
  x) reformat into what the test harness find palitable
  x) Profit


  NOTE:   I found interesting work on how to directly work with incomplete graphs:  http://homepage.univie.ac.at/ivana.ljubic/research/pcstp/
          But it's easier to transform the problem into canonical form and use standardized tools.
          for each of these steps, memory and computational complexity is well understood.

  COMPLEXITY:
          Time:  O(n^3)     for Floyd-Warshall shortest path calculations
          Space: O(n^2)     for Floyd-Warshall distance and 'next' matricies
          
          note: don't take these complexity assesment as gospel, I may be wrong.
                k-opt should be more efficient in both time and space dimensions.
'''


import json
import collections
import random
import floydwarshall


random.seed(42)


# utility objects for input sanitizing, distance calculation and random path generation
def clean_pt(s):
  return int(s[3:])


def output_format(i):
  return 'pt_{0}'.format(i)


def dist(p0, p1):
  ''' calculates the distance between two 2D points '''
  return ((p1.x - p0.x)**2 + (p1.y - p0.y)**2)**.5


def shuffle(lst):
  ''' returns a shuffled list instead of shuffling in place '''
  random.shuffle(lst)
  return lst


# utility named tuples
Point = collections.namedtuple('Point', ['id', 'x', 'y'])
Arc = collections.namedtuple('Arc', ['p0', 'p1'])


# deserialize the json into a python object
graph  = json.loads(open(r'./graph.json', 'rb').read())

points = [Point(i, p['x'], p['y']) for i, p in enumerate(graph['points'])]
arcs   = set(Arc(*map(clean_pt, arc)) for arc in graph['arcs'])

num_points = len(points)


# build a graph, G, in the cannonical (G[u][v] -> dist) form
G = {i:{j:dist(start, end) for j, end in enumerate(points) if not i == j and (j, i) in arcs or (i, j) in arcs} for i, start in enumerate(points)}


# use Floyd-Warshall to generate a complete graph
floyd      = floydwarshall.FloydWarshallWithPathReconstruction(G)
G_complete = floyd.as_complete_graph


# randomly initialize a path through the graph
starting_tour = shuffle([p.id for p in points])


# set up a cost tour function, needed to optimize a tour
def cost_of(t):
  ''' get the total distance traversed by a tour.
      don't forget to loop back to the zeroth item'''
  return sum(G_complete[t0][t1] for t0, t1 in zip(t[:-1], t[1:])) + G_complete[t[-1]][t[0]]


# use 2-opt to optimize a tour, walking downhill to a local minima
for i in range(num_points):
  for j in range(i):
    new_tour                 = starting_tour[:]
    new_tour[i], new_tour[j] = new_tour[j], new_tour[i]
    starting_cost, new_cost  = cost_of(starting_tour), cost_of(new_tour)
    if new_cost < starting_cost:
      #print 'found a better tour: {0} vs. {1}. Swapping {0} with {1}'.format(new_cost, starting_cost, i, j)
      starting_tour = new_tour


# rotate the solution to start at point_id 0, close the loop by tacking on 0 at the end
start         = starting_tour.index(0)
starting_tour = starting_tour[start:] + starting_tour[:start] + [0]


# use Floyd-Warshall to back out a path that includes all intermediate nodes
complete_tour = []
for i in range(len(starting_tour) - 1):
  complete_tour += [starting_tour[i]] + floyd.get_path(starting_tour[i], starting_tour[i+1])
complete_tour += [starting_tour[-1]]


# transform the tour into a format palitable to the test harness
final_tour = map(output_format, complete_tour)

print final_tour
