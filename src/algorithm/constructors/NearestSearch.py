from src.core.Solution import Solution
from src.algorithm.operators.LocalSearch import CreateRoute, InjectBefore, InjectAfter
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
        cache = solution.create_cache()
        create_route_op = CreateRoute(cache)
        inject_bef_op = InjectBefore(cache)
        inject_aft_op = InjectAfter(cache)

        # create a route for every vehicle and inject a random unassigned jobs
        for vehicle_idx in range(self.problem.num_vehicles):
            if len(solution.unassigned_jobs) == 0:
                break

            create_route_op.create(vehicle_idx, [random.choice(cache.unassigned_jobs)])
            if cache.eval_constraint():
                solution.accept_cache()

                # iteratively add the neighbour of the last job in the route if it is unassigned
                job = cache.get_route(vehicle_idx).jobs[-1]
                neighbour_index = 0
                while neighbour_index < len(cache.problem.neighbour_array[job]):
                    neighbour = cache.problem.neighbour_array[job][neighbour_index]
                    if neighbour in cache.unassigned_jobs:
                        inject_aft_op.move(job, neighbour)
                        if cache.eval_constraint():
                            solution.accept_cache()
                            job = neighbour
                            neighbour_index = 0
                        else:
                            solution.reset_cache()
                            neighbour_index += 1
                            logging.debug(f"{self.__class__.__name__}::failed to inject neighbour {neighbour}, recovering to last solution")
                    else:
                        neighbour_index += 1
            else:
                solution.reset_cache()

        # iteratively inject unassigned jobs if there is any
        solution.eval_unassigned_jobs()
        prev_num_unassigned = len(solution.unassigned_jobs)
        solution.reset_cache()
        while len(cache.unassigned_jobs) > 0:
            logging.debug(f"{self.__class__.__name__}::trying to inject {len(cache.unassigned_jobs)} unassigned jobs: {len(cache.unassigned_jobs)}")

            for unassigned in cache.unassigned_jobs:
                inject_successful = False
                for neighbour in cache.problem.neighbour_array[unassigned]:
                    if inject_successful:
                        break
                    if neighbour in cache.unassigned_jobs:
                        continue
                    for op in [inject_bef_op, inject_aft_op]:
                        op.move(neighbour, unassigned)
                        if cache.eval_constraint():
                            solution.accept_cache()
                            inject_successful = True
                            break
                        else:
                            solution.reset_cache()
                            logging.debug(f"{self.__class__.__name__}::failed to inject neighbour {neighbour}, recovering to last solution")

            if len(cache.unassigned_jobs) == prev_num_unassigned:
                break

        # final evaluation
        solution.eval_solution()
        if len(solution.unassigned_jobs) > 0:
            logging.info(f"{self.__class__.__name__}::final num of unassigned jobs: {len(solution.unassigned_jobs)}")

        return solution
