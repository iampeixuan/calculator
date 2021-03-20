from src.core.Model import Objective, Model


# define functions to retrieve the attributes
def get_depot_index(problem, vehicle_idx):
    return problem.get_vehicle_attr(vehicle_idx, problem.model.depot_index)


def get_capacity(problem, vehicle_idx):
    return problem.get_vehicle_attr(vehicle_idx, problem.model.capacity)


def get_start_time(problem, vehicle_idx):
    return problem.get_vehicle_attr(vehicle_idx, problem.model.start_time)


def get_end_time(problem, vehicle_idx):
    return problem.get_vehicle_attr(vehicle_idx, problem.model.end_time)


def get_ready_time(problem, node_idx):
    return problem.get_node_attr(node_idx, problem.model.ready_time)


def get_due_time(problem, node_idx):
    return problem.get_node_attr(node_idx, problem.model.due_time)


def get_demand(problem, node_idx):
    return problem.get_node_attr(node_idx, problem.model.demand)


def get_service_time(problem, node_idx):
    return problem.get_node_attr(node_idx, problem.model.service_time)


def get_cost(problem, prev_node_index, current_node_index):
    return problem.get_node_node_attr(prev_node_index, current_node_index, problem.model.cost)


# define objectives
def calc_num_unassigned_jobs(solution):
    return len(solution.unassigned_jobs)


def calc_num_vehicles(solution):
    num_vehicles = 0
    for route in solution.routes:
        if len(route.jobs) > 0:
            num_vehicles += 1

    return num_vehicles


def calc_distance(solution):
    solution_distance = 0.0
    for route in solution.routes:
        depot = get_depot_index(solution.problem, route.vehicle_idx)
        route_distance = 0.0
        prev_job = depot
        for job in route.jobs:
            route_distance += get_cost(solution.problem, prev_job, job)
            prev_job = job
        route_distance += get_cost(solution.problem, job, depot)
        solution_distance += route_distance

    return solution_distance


def calc_time(solution):
    solution_time = 0.0
    for route in solution.routes:
        depot = get_depot_index(solution.problem, route.vehicle_idx)
        route_time = 0.0
        prev_job = depot
        leave_time = get_start_time(solution.problem, route.vehicle_idx)
        for job in route.jobs:
            cost = get_cost(solution.problem, prev_job, job)
            service_time = get_service_time(solution.problem, job)
            ready_time = get_ready_time(solution.problem, job)

            arrival_time = leave_time + cost
            waiting_time = max(0, ready_time - arrival_time)
            leave_time = arrival_time + waiting_time + service_time
            route_time += (cost + waiting_time + service_time)
            prev_job = job
        route_time += get_cost(solution.problem, job, depot)
        solution_time += route_time

    return solution_time


# define constraints
def time_window_constraint(solution):
    for route in solution.routes:
        depot = get_depot_index(solution.problem, route.vehicle_idx)
        prev_job = depot
        leave_time = get_start_time(solution.problem, route.vehicle_idx)
        for job in route.jobs:
            cost = get_cost(solution.problem, prev_job, job)
            service_time = get_service_time(solution.problem, job)
            ready_time = get_ready_time(solution.problem, job)
            due_time = get_due_time(solution.problem, job)

            arrival_time = leave_time + cost
            waiting_time = max(0, ready_time - arrival_time)
            delay_time = max(0, arrival_time - due_time)
            leave_time = arrival_time + waiting_time + service_time
            prev_job = job
            if delay_time > 0:
                return False

        end_time = leave_time + get_cost(solution.problem, job, depot)
        if end_time > get_end_time(solution.problem, route.vehicle_idx):
            return False

    return True


def vehicle_capacity_constraint(solution):
    for route in solution.routes:
        vehicle_capacity = get_capacity(solution.problem, route.vehicle_idx)
        route_demand = 0.0
        for job in route.jobs:
            route_demand += get_demand(solution.problem, job)
            if route_demand > vehicle_capacity:
                return False

    return True


# define the attributes, objectives and constraints related to Homberger
class Homberger(Model):
    global_attributes = []
    vehicle_attributes = ["capacity", "start_time", "end_time", "depot_index"]
    node_attributes = ["x", "y", "demand", "ready_time", "due_time", "service_time"]
    node_node_attributes = ["cost"]
    vehicle_node_node_attributes = []
    objectives = [Objective(calc_num_unassigned_jobs, "num_unassigned_jobs"),
                  Objective(calc_num_vehicles, "num_vehicles"),
                  Objective(calc_distance, "distance"),
                  Objective(calc_time, "time")]
    constraints = [time_window_constraint, vehicle_capacity_constraint]
