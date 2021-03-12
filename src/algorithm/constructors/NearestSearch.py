from src.core.Solution import Solution, Route
import random
import logging


class NearestSearch:
    def __init__(self, problem, **kwargs):
        self.problem = problem
        self.neighbourhood_size = kwargs.get("neighbourhood_size", self.problem.num_nodes)
        self.seed = kwargs.get("seed", None)
        random.seed(self.seed)

    def solve(self):
        if not self.problem.neighbour_array:
            self.problem.update_neighbour(self.neighbourhood_size)

        # best_solution is to return, solution is to be worked on
        best_solution = Solution(self.problem)
        best_solution.eval_solution()
        solution = best_solution.copy()
        logging.info(f"initial num of unassigned jobs: {len(best_solution.unassigned_jobs)}")

        # create a route for every vehicle and inject unassigned jobs
        for vehicle_idx in range(self.problem.num_vehicles):
            if len(best_solution.unassigned_jobs) == 0:
                break

            if create_route(solution, vehicle_idx):
                best_solution.assigned_by(solution)

                # try to add the closest neighbour to the end of the route
                while add_neighbour(solution, solution.get_route(vehicle_idx)):
                    best_solution.assigned_by(solution)
                solution.assigned_by(best_solution)
            else:
                solution.assigned_by(best_solution)

        # evaluate the best solution and return
        best_solution.eval_solution()
        logging.info(f"final num of unassigned jobs: {len(best_solution.unassigned_jobs)}")

        return best_solution


def create_route(solution, vehicle_idx):
    if len(solution.unassigned_jobs) == 0:
        logging.debug("solution has no unassigned jobs")
        return False

    job_idx = random.choice(solution.unassigned_jobs)
    route = Route(vehicle_idx, [job_idx])
    logging.debug(f"creating a route with vehicle_idx: {vehicle_idx}, job_idx: {job_idx}")

    solution.routes.append(route)
    if solution.eval_constraint():
        solution.eval_unassigned_jobs()
        logging.debug("route created successfully")
        return True
    else:
        route.clear_jobs()
        logging.debug("failed to create route")
        return False


def add_neighbour(solution, route):
    job_idx = route.jobs[-1]
    for i in range(len(solution.problem.neighbour_array[job_idx])):
        neighbour_idx = solution.problem.neighbour_array[job_idx][i]
        if neighbour_idx in solution.unassigned_jobs:
            route.jobs.append(neighbour_idx)
            if solution.eval_constraint():
                solution.eval_unassigned_jobs()
                logging.debug(f"add {neighbour_idx} after {job_idx} successfully")
                return True
            else:
                route.jobs.pop()

    return False
