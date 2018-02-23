from collections import deque
from random import randrange

def tabucol(graph, number_of_colors, tabu_size=7, reps=100, max_iterations=10000, debug=False):
    # graph is assumed to be the adjacency matrix of an undirected graph with no self-loops
    # nodes are represented with indices, [0, 1, ..., n-1]
    # colors are represented by numbers, [0, 1, ..., k-1]
    colors = list(range(number_of_colors))
    # number of iterations of the tabucol algorithm
    iterations = 0
    # initialize tabu as empty queue
    tabu = deque()
    
    # solution is a map of nodes to colors
    # Generate a random solution:
    solution = dict()
    for i in range(len(graph)):
        solution[i] = colors[randrange(0, len(colors))]

    # Aspiration level A(z), represented by a mapping: f(s) -> best f(s') seen so far
    aspiration_level = dict()

    while iterations < max_iterations:
        # Count node pairs (i,j) which are adjacent and have the same color.
        move_candidates = set()  # use a set to avoid duplicates
        conflict_count = 0
        for i in range(len(graph)):
            for j in range(i+1, len(graph)):  # assume undirected graph, ignoring self-loops
                if graph[i][j] > 0: # adjacent
                    if solution[i] == solution[j]:  # same color
                        move_candidates.add(i)
                        move_candidates.add(j)
                        conflict_count += 1
        move_candidates = list(move_candidates)  # convert to list for array indexing

        if conflict_count == 0:
            # Found a valid coloring.
            break

        # Generate neighbor solutions.
        new_solution = None
        for r in range(reps):
            # Choose a node to move.
            node = move_candidates[randrange(0, len(move_candidates))]
            
            # Choose color other than current.
            new_color = colors[randrange(0, len(colors) - 1)]
            if solution[node] == new_color:
                # essentially swapping last color with current color for this calculation
                new_color = colors[-1]

            # Create a neighbor solution
            new_solution = solution.copy()
            new_solution[node] = new_color
            # Count adjacent pairs with the same color in the new solution.
            new_conflicts = 0
            for i in range(len(graph)):
                for j in range(i+1, len(graph)):
                    if graph[i][j] > 0 and new_solution[i] == new_solution[j]:
                        new_conflicts += 1
            if new_conflicts < conflict_count:  # found an improved solution
                # if f(s') <= A(f(s)) [where A(z) defaults to z - 1]
                if new_conflicts <= aspiration_level.setdefault(conflict_count, conflict_count - 1):
                    # set A(f(s) = f(s') - 1
                    aspiration_level[conflict_count] = new_conflicts - 1

                    if (node, new_color) in tabu: # permit tabu move if it is better any prior
                        tabu.remove((node, new_color))
                        if debug:
                            print("tabu permitted;", conflict_count, "->", new_conflicts)
                        break
                else:
                    if (node, new_color) in tabu:
                        # tabu move isn't good enough
                        continue
                if debug:
                    print (conflict_count, "->", new_conflicts)
                break

        # At this point, either found a better solution,
        # or ran out of reps, using the last solution generated
        
        # The current node color will become tabu.
        # add to the end of the tabu queue
        tabu.append((node, solution[node]))
        if len(tabu) > tabu_size:  # queue full
            tabu.popleft()  # remove the oldest move

        # Move to next iteration of tabucol with new solution
        solution = new_solution
        iterations += 1
        if debug and iterations % 500 == 0:
            print("iteration:", iterations)

    #print("Aspiration Levels:\n" + "\n".join([str((k,v)) for k,v in aspiration_level.items() if k-v > 1]))

    # At this point, either conflict_count is 0 and a coloring was found,
    # or ran out of iterations with no valid coloring.
    if conflict_count != 0:
        print("No coloring found with {} colors.".format(number_of_colors))
        return None
    else:
        print("Found coloring:\n", solution)
        return solution

try:
    import matplotlib.pyplot as plt
    import networkx as nx

    def load_testcase(file):
        graph = nx.Graph()
        with open(file, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                words = line.split()
                if words[0] == 'p':
                    assert words[1] == 'edge'
                    vertices = int(words[2])
                    graph.add_nodes_from(range(vertices))
                if words[0] == 'e':
                    graph.add_edge(int(words[1]) - 1, int(words[2]) - 1)
        return graph
                
    def test(nx_graph, k, draw=False):
        graph = nx.to_numpy_matrix(nx_graph).astype(int).tolist()
        coloring = tabucol(graph, k, debug=True)
        if draw:
            values = [coloring[node] for node in nx_graph]
            nx.draw(nx_graph, node_color=values, pos=nx.shell_layout(nx_graph))
            plt.show()
except ImportError:
    print("Need networkx and matplotlib installed for testing.")

if __name__ == "__main__":
    graph = [[0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0],
             [1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0],
             [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0],
             [0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],
             [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0],
             [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1],
             [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1],
             [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
             [0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0],
             [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1],
             [0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0],
             [0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0]]
    test(nx.chvatal_graph(), 4, True)
