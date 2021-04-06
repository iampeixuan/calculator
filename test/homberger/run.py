import math
from src.core.Problem import Problem
from src.algorithm.constructors.NearestSearch import NearestSearch
from src.algorithm.metaheuristics.Ils import Ils
from Homberger import Homberger, get_cost
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


def get_problem(file_path):
    with open(file_path) as f:
        line = f.readline()
        while line:
            if "VEHICLE" in line:
                _ = f.readline()
                numbers = [element for element in f.readline().replace("\n", "").split(" ") if element.isnumeric()]
                num_vehicles = int(numbers[0])
                capacity = int(numbers[1])
            elif "CUSTOMER" in line:
                _ = f.readline()
                _ = f.readline()
                node_data = []
                while True:
                    numbers = [element for element in f.readline().replace("\n", "").split(" ") if element.isnumeric()]
                    if len(numbers) == 7:
                        node_data.append(numbers)
                    else:
                        break
            line = f.readline()

    # convert input to problem
    depot_indexes = [0]
    global_attrs = {"wait_for_ready": True}
    vehicles_with_attrs = [{"capacity": capacity,
                            "start_time": int(node_data[0][4]),
                            "end_time": int(node_data[0][5]),
                            "depot_index": 0}] * num_vehicles
    nodes_with_attrs = [{"x": int(data[1]),
                         "y": int(data[2]),
                         "demand": int(data[3]),
                         "ready_time": int(data[4]),
                         "due_time": int(data[5]),
                         "service_time": int(data[6])} for data in node_data]
    cost_matrix = []
    for data1 in node_data:
        x1, y1 = int(data1[1]), int(data1[2])
        cost_array = []
        for data2 in node_data:
            x2, y2 = int(data2[1]), int(data2[2])
            cost = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            cost_array.append(cost)
        cost_matrix.append(cost_array)

    node_node_attrs = {"cost": cost_matrix}
    vehicle_node_node_attrs = {}

    return Problem(Homberger().create(), depot_indexes, global_attrs, vehicles_with_attrs, nodes_with_attrs, node_node_attrs, vehicle_node_node_attrs)


if __name__ == "__main__":
    # generate problem
    path = "problems/C1_2_1.TXT"
    problem = get_problem(path)
    problem.set_closeness(get_cost)

    # run algorithm and generate solution
    nearest_search = NearestSearch(problem, neighbourhood_size=50, seed=0)
    solution = nearest_search.solve()

    ils = Ils(problem, max_iter=10, max_time=3, log_freq=1, neighbourhood_size=50, seed=0)
    ils.set_initial_solution(solution)
    solution = ils.solve()

    print(solution)

    # ---------- test cases ----------
    # solution1 = Solution(problem)
    # solution1.routes.append(Route(jobs=[2]))
    # solution1.eval_objective()
    #
    # solution2 = Solution(problem)
    # solution2.routes.append(Route(jobs=[2]))
    # solution2.eval_objective()
    #
    # print("solution1 equals solution2:", solution1.equals(solution2))
    # print("solution1 == solution2:", solution1 == solution2)
    # print("solution1 > solution2:", solution1 > solution2)
    #
    # print("solution1 objectives:", solution1.objectives_output)
    # print("solution1 is_feasible:", solution1.is_feasible)
    #
    # print("solution2 objectives:", solution2.objectives_output)
    # print("solution2 is_feasible:", solution2.is_feasible)
