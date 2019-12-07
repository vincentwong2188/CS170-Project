import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils
from collections import defaultdict

from student_utils import *
from queue import LifoQueue
"""
======================================================================
  Complete the following function.
======================================================================
"""

def solve(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, params=[]):
    """
    Write your algorithm here.
    Input:
        list_of_locations: A list of locations such that node i of the graph corresponds to name at index i of the list
        list_of_homes: A list of homes
        starting_car_location: The name of the starting location for the car
        adjacency_matrix: The adjacency matrix from the input file
    Output:
        A list of locations representing the car path
        A dictionary mapping drop-off location to a list of homes of TAs that got off at that particular location
        NOTE: both outputs should be in terms of indices not the names of the locations themselves
    """

    starting_car_index = list_of_locations.index(starting_car_location)
    list_homes_index = [list_of_locations.index(home) for home in list_of_locations if home in list_of_homes]

    mst = Mst(adjacency_matrix)
    
    # mst = adjacency_matrix

    # leaf_nodes = []
        
    # if starting_car_index in leaf_nodes:
    #     leaf_nodes.remove(starting_car_index)

    # for node in leaf_nodes:
    #     if node not in list_homes_index:
    #         mst.remove_node(node)
            # print('removed: ' + str(node))

    path, output = DFS(mst, starting_car_index, list_homes_index)

    g, message = adjacency_matrix_to_graph(adjacency_matrix)

    # print('g edges: {}'.format(g.edges))
    # print('mst edges: {}'.format(mst.edges))

    # print('path: {}'.format(path))

    # print('output: {}'.format(output))
    return path, output


def DFS(G, start, list_of_homes):
    current = start
    visited = []
    fringe = LifoQueue(maxsize = G.number_of_nodes())
    people_remaining = list_of_homes
    temp = people_remaining.copy()
    output = defaultdict(list)
    path = []

    
    predecessors, distances = nx.floyd_warshall_predecessor_and_distance(G)
      

    while len(people_remaining) > 0:

        # drop off TA from car 
        if current in list_of_homes:
            output[current].append(current)
            people_remaining.remove(current)
            # print('node {} dropped'.format(current))

        #mark current as visited
        visited.append(current)
        unvisited_neighbors = []

        # print('current node: {}'.format(current))

        #check neighbors for not visited
        for node in G.neighbors(current):
            if node not in visited:
                unvisited_neighbors.append(node)
        # print('neighbors: {}'.format(G.neighbors(current)))
        # print('unvisited neighbors: {}'.format(unvisited_neighbors))

        #check how many TAs that path helps
        for i in unvisited_neighbors:
            # print('current neighbor: {}'.format(i))
            ta_homes_along_path = []
            if people_remaining:
                for j in people_remaining:
                    if (distances[i][j] - distances[current][j]) < 0: # ('helps a dude')
                        ta_homes_along_path.append(j)
                if len(ta_homes_along_path) == 1: #('helps less than 1 dude' so i drop him
                    output[current].append(ta_homes_along_path[0])
                    people_remaining.remove(ta_homes_along_path[0])
                    # print('node {} dropped'.format(j))
                elif len(ta_homes_along_path) == 0:
                    continue
                else: 
                    fringe.put(i)
                    # print('{} added to fringe'.format(i))
        
        # print('people remaning: {}'.format(people_remaining))
        if fringe.empty():
            # print('fringe empty. new_path : {}'.format(nx.reconstruct_path(current, start, predecessors)))
            path = path + (nx.reconstruct_path(current, start, predecessors))

            if current == start:
                path = path + [start]
        else:
            next_item = fringe.get()
            new_path = nx.reconstruct_path(current, next_item, predecessors)
            # print('new path: {}'.format(new_path))
            path = path + (new_path)
            path.pop()
            current = next_item

    return path, output



def Mst(adjacency_matrix):
    g, message = adjacency_matrix_to_graph(adjacency_matrix)
    mst = nx.minimum_spanning_tree(g)
    mst_adj_matrix = nx.to_numpy_matrix(mst).tolist()

    for i in range(len(mst_adj_matrix)): #for each row
        for j in range(len(mst_adj_matrix[0])): #for each col
            if mst_adj_matrix[i][j] == 0:
                # print(mst_adj_matrix[i,j])
                mst_adj_matrix[i][j] = 'x' 

    g_out, message = adjacency_matrix_to_graph(mst_adj_matrix)
    return g_out

"""
======================================================================
   No need to change any code below this line
======================================================================
"""

"""
Convert solution with path and dropoff_mapping in terms of indices
and write solution output in terms of names to path_to_file + file_number + '.out'
"""
def convertToFile(path, dropoff_mapping, path_to_file, list_locs):
    string = ''
    for node in path:
        string += list_locs[node] + ' '
    string = string.strip()
    string += '\n'

    dropoffNumber = len(dropoff_mapping.keys())
    string += str(dropoffNumber) + '\n'
    for dropoff in dropoff_mapping.keys():
        strDrop = list_locs[dropoff] + ' '
        for node in dropoff_mapping[dropoff]:
            strDrop += list_locs[node] + ' '
        strDrop = strDrop.strip()
        strDrop += '\n'
        string += strDrop
    utils.write_to_file(path_to_file, string)

def solve_from_file(input_file, output_directory, params=[]):
    print('Processing', input_file)

    input_data = utils.read_file(input_file)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(input_data)
    car_path, drop_offs = solve(list_locations, list_houses, starting_car_location, adjacency_matrix, params=params)

    basename, filename = os.path.split(input_file)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = utils.input_to_output(input_file, output_directory)

    convertToFile(car_path, drop_offs, output_file, list_locations)


def solve_all(input_directory, output_directory, params=[]):
    input_files = utils.get_files_with_extension(input_directory, 'in')

    for input_file in input_files:
        solve_from_file(input_file, output_directory, params=params)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--all', action='store_true', help='If specified, the solver is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', type=str, help='The path to the input file or directory')
    parser.add_argument('output_directory', type=str, nargs='?', default='.', help='The path to the directory where the output should be written')
    parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    output_directory = args.output_directory
    if args.all:
        input_directory = args.input
        solve_all(input_directory, output_directory, params=args.params)
    else:
        input_file = args.input
        solve_from_file(input_file, output_directory, params=args.params)
