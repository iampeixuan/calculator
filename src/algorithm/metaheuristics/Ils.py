from src.core.Solution import Solution
from src.algorithm.operators.LocalSearchOperator import InjectBefore, InjectAfter, TwoOpt, TwoPoint
from time import time
import random
import logging


class Ils:
    def __init__(self, problem, **kwargs):
        self.problem = problem
        self.max_iter = kwargs.get("max_iter", 10)
        self.max_time = kwargs.get("max_time", 3.0)
        self.log_freq = kwargs.get("log_freq", 1)
        self.neighbourhood_size = kwargs.get("neighbourhood_size", self.problem.num_nodes)
        self.seed = kwargs.get("seed", None)
        random.seed(self.seed)
        self.init_solution = None
        self.solution = None
        self.best_solution = None

    def set_initial_solution(self, solution):
        self.init_solution = solution
        if self.init_solution.problem != self.problem:
            logging.error(f"{self.__class__.__name__}::input problem does not match with initial solution")
            exit(1)

    def solve(self):
        start_time = time()
        if not self.problem.neighbour_array or len(self.problem.neighbour_array[0]) != self.neighbourhood_size:
            self.problem.update_neighbour(self.neighbourhood_size)
        if not self.init_solution:
            self.solution = Solution(self.problem)
        else:
            self.solution = self.init_solution.copy()

        self.solution.eval_solution()
        self.best_solution = self.solution.copy()
        cache = self.solution.copy()
        logging.info(f"{self.__class__.__name__}::initial solution: {self.solution}")

        inject_bef_op = InjectBefore(cache)
        inject_aft_op = InjectAfter(cache)
        two_opt_op = TwoOpt(cache)
        two_point_op = TwoPoint(cache)

        for i in range(self.max_iter):
            for op in [inject_bef_op, inject_aft_op]:
                self.inject_unassigned(op)

            # run uphill
            for op in [inject_bef_op, inject_aft_op, two_point_op, two_opt_op]:
                for job in cache.problem.job_indexes:
                    self.local_search(op, job, uphill=True)
                if self.solution.better_than(self.best_solution):
                    self.best_solution.assigned_by(self.solution)
                if i % self.log_freq == 0:
                    logging.info(f"{self.__class__.__name__}::iter={i}-u-{op.__class__.__name__:12}: {self.best_solution}")
                if time() - start_time > self.max_time * 60:
                    return self.best_solution

            # run downhill
            for op in [inject_bef_op, inject_aft_op, two_point_op, two_opt_op]:
                for job in cache.problem.job_indexes:
                    self.local_search(op, job, uphill=False)
                if self.solution.better_than(self.best_solution):
                    self.best_solution.assigned_by(self.solution)
                if i % self.log_freq == 0:
                    logging.info(f"{self.__class__.__name__}::iter={i}-d-{op.__class__.__name__:12}: {self.best_solution}")
                if time() - start_time > self.max_time * 60:
                    return self.best_solution

        return self.best_solution

    def inject_unassigned(self, operator):
        num_unassigned = len(operator.solution.unassigned_jobs)
        if num_unassigned == 0:
            return
        else:
            for unassigned in operator.solution.unassigned_jobs:
                for job in operator.solution.problem.job_indexes:
                    if job in operator.solution.unassigned_jobs or job == unassigned:
                        continue
                    operator.move(job, unassigned)
                    if operator.check_feasible():
                        break
                    else:
                        operator.recover()

            if len(operator.solution.unassigned_jobs) < num_unassigned:
                self.solution.assigned_by(operator.solution)

    def local_search(self, operator, job, uphill):
        uphill_index = -1
        neighbours = operator.solution.problem.neighbour_array[job]
        for neighbour in neighbours:
            operator.move(job, neighbour)
            if operator.eval_and_check_feasible():
                if operator.solution.better_than(self.solution):
                    self.solution.assigned_by(operator.solution)
                    return
            else:
                operator.recover()
