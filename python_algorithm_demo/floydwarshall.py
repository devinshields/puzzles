#!/usr/bin/python


import copy


class FloydWarshallWithPathReconstruction(object):
  ''' taken directly from: http://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm '''

  def __init__(self, G):
    ''' copies the original graph & runs the algo. Assumes keys are 0 - N-1 and that distances are symmetric. '''
    self.G    = copy.deepcopy(G)
    key_count = len(G.keys())
    self.key_count = key_count
    # init the distance matrix
    self.dist = [[float('inf') for i in range(key_count)] for i in range(key_count)]
    # init the next matrix
    self.next = [[None for i in range(key_count)] for i in range(key_count)]
    #
    self._run_()
    pass


  @property
  def as_complete_graph(self):
    ''' uses node-to-node shorest path distances to create a virtual complete graph.
        You're trading sparsity for the ability to feed this into any standard TSP solver. '''
    return {i:{j:self.dist[i][j] for j in range(self.key_count) if not i == j} for i in range(self.key_count)}


  def _run_(self):
    ''' runs the algorithm so that later property access will give correct results. Is called when the object is initialized. '''
    # set node self distance to 0
    for v in self.G.keys():
      self.dist[v][v] = 0
    # set distances for real edges
    for v in self.G.keys():
      for u in self.G[v]:
        self.dist[v][u] = self.G[v][u]
    # the meat of the algo - if a calculated distance is less than the current one, update the dist and next matricies. O(N^3).
    for k in range(self.key_count):
      for i in range(self.key_count):
        for j in range(self.key_count):
          if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
            self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
            self.next[i][j] = k
    pass


  def get_path(self, i, j):
    ''' returns a list containing the shortest path from node i to node j, exclusive of i & j.
        example: get_path(1,3) -> 2. where the original shortest path is 1 -> 2 -> 3.
        returned values are meant to reside in between in an original non-adjacent tour.'''
    intermediate = self.next[i][j]
    if intermediate is None:
      assert self.G[i][j] > 0
      return [] #  direct edge is fastest
    # recursively build out the path
    return self.get_path(i, intermediate) + [intermediate] + self.get_path(intermediate, j)


  pass



if __name__ == "__main__":
  main()
