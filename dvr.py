# Name: Kaushal Lodd
# Roll No: BT19CSE052

from collections import defaultdict, deque
import sys
import threading
import math
import time
from copy import deepcopy

# Router Class that contains all relevant information about a router instance
class Router:
    # Constructor
    def __init__(self, name) -> None:
        # Unique name for the router
        self.name = name

        # Shared queue
        self.queue = deque()

        # Lock for shared queue
        self.queue_lock = threading.Lock()

        # Number of iterations
        self.iterations = 0

        # List of neighbour routers
        self.neighbours = []

        # Map that stores router name as key and iteration number when it was appended as value
        self.appended_at = defaultdict(lambda: None)

        # Routing Table, a defaultdict that maps a dest router to its [<cost>, <path>] value
        # If missing key, it gives default value of [math.inf, '[no path]']
        self.table = defaultdict(lambda: [math.inf, '[no path]'])
        self.table[name] = 0, 'None' # Distance to itself is 0


    # Method to print Router object as a String
    def __str__(self) -> str:
        s = [
            "Router Object",
            f"Name: {self.name}",
            f"Neighbours: {self.neighbours}",
            "Routing Table: {",
        ]

        for router_name in sorted(routers):
            # Generates all default values for whatever doesn't exist (since we use defaultdict)
            _, _ = self.table[router_name]

        for router_name in sorted(self.table.keys()):
            cost = self.table[router_name][0]
            x = "   "
            x += "*" if self.appended_at[router_name] == self.iterations else " "
            s.append(f"{x}{router_name}: {cost:<10} via: {self.table[router_name][1]}")

        s.append("}")
        return "\n".join(s)

    
    # Method to append names of neigbouring routers into instance variable neighbours
    def add_neighbours(self, name):
        self.neighbours.append(name)


# Method that parses the input.txt file and populates the routers dict
def input_parser(filename):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

            no_of_routers = int(lines[0])

            routerNames = lines[1].split()
            for name in routerNames:
                routers[name] = Router(name)
            
            lines = lines[2:]
            lines.pop() if "EOF" in lines[-1] else None

            for line in lines:
                src, dest, cost = map(
                    lambda x: int(x[1]) if x[0] == 2 else x[1], enumerate(line.split())
                )

                routers[src].add_neighbours(dest)
                routers[src].table[dest][0] = cost
                routers[src].table[dest][1] = dest

                routers[dest].add_neighbours(src)
                routers[dest].table[src][0] = cost
                routers[dest].table[src][1] = src
    except:
        raise SyntaxError('Check input file for Syntax error.')
    

# Method to run after creating a thread
def threaded(router_name):
    router = routers[router_name]
    add_to_queue(router_name)

    # Waiting for add_to_queue to finish
    while True:
        if len(router.queue) == len(router.neighbours):
            break
    
    # Implementing the Bellman-Ford Equation
    # Increasing iteration value
    router.iterations += 1

    table_copy = deepcopy(router.table)
    for table, name in router.queue:
        for eachRouter in routers:
            val = table[eachRouter][0] + router.table[name][0]

            # Updating least-costly path
            if val < table_copy[eachRouter][0]:
                table_copy[eachRouter][0] = val
                table_copy[eachRouter][1] = table_copy[name][1]

    for key, value in table_copy.items():
        if router.table[key] != value:
            router.table[key] = value
            router.appended_at[key] = router.iterations

    router.queue.clear()
    time.sleep(2)


# Append router table, router name of each neighbour in the queue of the router
def add_to_queue(router_name):
    for nhbr in routers[router_name].neighbours:
        with routers[nhbr].queue_lock:
            routers[nhbr].queue.append((deepcopy(routers[router_name].table), router_name))


# Map containing name of router as key and the router object as value
routers = dict()

# Main function
if __name__ == '__main__':
    try:
        _, filename = sys.argv
    except:
        print('Error! Usage: python dvr.py filename')
    else:
        # parsing input.txt
        input_parser(filename)

        # Printing routers before updation
        print(f'\n******** Iteration 0 *********\n')
        for key, value in routers.items():
            print(f'{key} => {value}\n')

        
        # Printing 4 iterations of updation
        for itr in range(1, 5):
            threads = []
            for router_name in routers:
                thread = threading.Thread(target = threaded, args = (router_name, ))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
            
            print(f'\n******** Iteration {itr} *********\n')
            for key, value in routers.items():
                print(f'{key} => {value}\n')
