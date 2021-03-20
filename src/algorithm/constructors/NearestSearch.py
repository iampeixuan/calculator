from src.core.Solution import Solution
from src.algorithm.operators.LocalSearch import CreateRoute, InjectAfter
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
        create_route_op = CreateRoute()
        create_route_op.set_solution(cache)
        inject_aft_op = InjectAfter()
        inject_aft_op.set_solution(cache)

        # create a route for every vehicle and inject a random unassigned jobs
        for vehicle_idx in range(self.problem.num_vehicles):
            if len(solution.unassigned_jobs) == 0:
                break

            create_route_op.create(vehicle_idx, [random.choice(cache.unassigned_jobs)])
            if cache.eval_constraint():
                solution.accept_cache()

                # try to add the closest neighbour of the last job in the route if it is unassigned
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
                            logging.debug(f"{self.__class__.__name__}::add neighbour {neighbour} failed, recovering to last solution")
                    else:
                        neighbour_index += 1
            else:
                solution.reset_cache()

        # evaluate the best solution and return
        solution.eval_solution()
        logging.info(f"{self.__class__.__name__}::final num of unassigned jobs: {len(solution.unassigned_jobs)}")

        return solution
