from src.core.Solution import Solution
from src.algorithm.operators.LocalSearchOperator import CreateRoute, InjectBefore, InjectAfter
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

        solution = Solution(self.problem)
        solution.eval_solution()
        logging.info(f"{self.__class__.__name__}::initial num of unassigned jobs: {len(solution.unassigned_jobs)}")

        # initialize the required operators
        cache = solution.copy()
        create_route_op = CreateRoute(cache)
        inject_bef_op = InjectBefore(cache)
        inject_aft_op = InjectAfter(cache)

        # create a route for every vehicle and inject a random unassigned jobs
        for vehicle_idx in range(self.problem.num_vehicles):
            if len(cache.unassigned_jobs) == 0:
                break

            create_route_op.move(vehicle_idx, random.choice(cache.unassigned_jobs))
            if create_route_op.check_feasible():
                solution.assigned_by(cache)

                # iteratively add the neighbour of the last job in the route if it is unassigned
                job = cache.get_route(vehicle_idx).jobs[-1]
                neighbour_index = 0
                while neighbour_index < len(cache.problem.neighbour_array[job]):
                    neighbour = cache.problem.neighbour_array[job][neighbour_index]
                    if neighbour in cache.unassigned_jobs:
                        inject_aft_op.move(job, neighbour)
                        if inject_aft_op.check_feasible():
                            solution.assigned_by(cache)
                            job = neighbour
                            neighbour_index = 0
                        else:
                            inject_aft_op.recover()
                            neighbour_index += 1
                            logging.debug(f"{self.__class__.__name__}::failed to inject neighbour {neighbour}, recovering...")
                    else:
                        neighbour_index += 1
            else:
                create_route_op.recover()

        # iteratively inject unassigned jobs if there is any
        cache.eval_solution()
        prev_num_unassigned = len(cache.unassigned_jobs)
        while len(cache.unassigned_jobs) > 0:
            logging.debug(f"{self.__class__.__name__}::trying to inject {len(cache.unassigned_jobs)} unassigned jobs")

            for unassigned in cache.unassigned_jobs:
                inject_successful = False
                for neighbour in cache.problem.neighbour_array[unassigned]:
                    if inject_successful:
                        break
                    if neighbour in cache.unassigned_jobs:
                        continue
                    for op in [inject_bef_op, inject_aft_op]:
                        op.move(neighbour, unassigned)
                        if op.check_feasible():
                            solution.assigned_by(cache)
                            inject_successful = True
                            break
                        else:
                            op.recover()
                            logging.debug(f"{self.__class__.__name__}::failed to inject neighbour {neighbour}, recovering...")

            if len(cache.unassigned_jobs) == prev_num_unassigned:
                break

        # final evaluation
        solution.assigned_by(cache)
        solution.eval_solution()
        logging.info(f"{self.__class__.__name__}::final num of unassigned jobs: {len(solution.unassigned_jobs)}")

        return solution
