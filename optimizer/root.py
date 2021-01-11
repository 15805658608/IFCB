#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu" at 15:35, 06/01/2021                                                               %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Nguyen_Thieu2                                  %
#       Github:     https://github.com/thieu1995                                                        %
# ------------------------------------------------------------------------------------------------------%

from numpy import array, ptp
from numpy.random import uniform
from time import time
from copy import deepcopy
from config import Config
from model.fitness import Fitness
from utils.schedule_util import matrix_to_schedule


class Root:
    ID_SOL = 0
    ID_FIT = 1

    def __init__(self, problem=None, pop_size=10, epoch=2, func_eval=100000, time_bound=None, domain_range=None):
        self.problem = problem
        self.pop_size = pop_size
        self.epoch = epoch
        self.func_eval = func_eval
        self.time_bound = time_bound
        self.domain_range = domain_range
        self.Fit = Fitness(problem)

    def create_solution(self):
        while True:
            matrix_cloud = uniform(self.domain_range[0], self.domain_range[1], (len(self.problem.tasks), len(self.problem.clouds)))
            matrix_fog = uniform(self.domain_range[0], self.domain_range[1], (len(self.problem.tasks), len(self.problem.fogs)))
            schedule = matrix_to_schedule(self.problem, matrix_cloud, matrix_fog)
            if schedule.is_valid():
                fitness = self.Fit.fitness(schedule)
                break
        return [[matrix_cloud, matrix_fog], fitness]        # [solution, fit]

    def early_stopping(self, array, patience=5):
        if patience <= len(array) - 1:
            value = array[len(array) - patience]
            arr = array[len(array) - patience + 1:]
            check = 0
            for val in arr:
                if val < value:
                    check += 1
            if check != 0:
                return False
            return True
        raise ValueError

    def get_index_roulette_wheel_selection(self, list_fitness: list):
        """ It can handle negative also. Make sure your list fitness is 1D-numpy array"""
        list_fitness = array(list_fitness)
        scaled_fitness = (list_fitness - min(list_fitness)) / ptp(list_fitness)
        minimized_fitness = 1.0 - scaled_fitness
        total_sum = sum(minimized_fitness)
        r = uniform(low=0, high=total_sum)
        for idx, f in enumerate(minimized_fitness):
            r = r + f
            if r > total_sum:
                return idx

    def evolve(self, pop):
        pass

    def train(self):
        print(f'Start training with: {self.__class__} algorithm')
        pop = [self.create_solution() for _ in range(self.pop_size)]
        if Config.METRICS == 'trade-off':
            g_best = max(pop, key=lambda x: x[self.ID_FIT])
        else:
            g_best = min(pop, key=lambda x: x[self.ID_FIT])
        g_best_list = [g_best[self.ID_FIT]]
        if Config.MODE == 'epoch':
            print(f'Training algorithm by: epoch (mode) with: {self.epoch} epochs')
            for epoch in range(self.epoch):
                time_epoch_start = time()
                pop = self.evolve(pop)
                if Config.METRICS == 'trade-off':
                    current_best = max(pop, key=lambda x: x[self.ID_FIT])
                    if current_best[self.ID_FIT] > g_best_list[-1]:
                        g_best = deepcopy(current_best)
                else:
                    current_best = min(pop, key=lambda x: x[1])
                    if current_best[self.ID_FIT] < g_best_list[-1]:
                        g_best = deepcopy(current_best)
                g_best_list.append(g_best[self.ID_FIT])
                time_epoch_end = time() - time_epoch_start
                print(f'Current best fit {current_best[self.ID_FIT]:.4f}, '
                      f'Global best fit {g_best[self.ID_FIT]:.4f}, '
                      f'Epoch {epoch + 1} with time: {time_epoch_end:.2f}')
            return g_best[0], g_best[1], array(g_best_list)
        elif Config.MODE == 'time':
            print(f'Training algorithm by: time (mode) with: {self.time_bound} seconds')
            time_bound_start = time()
            for epoch in range(self.epoch):
                time_epoch_start = time()
                pop = self.evolve(pop)
                if Config.METRICS == 'trade-off':
                    current_best = max(pop, key=lambda x: x[self.ID_FIT])
                    if current_best[self.ID_FIT] > g_best_list[-1]:
                        g_best = deepcopy(current_best)
                else:
                    current_best = min(pop, key=lambda x: x[1])
                    if current_best[self.ID_FIT] < g_best_list[-1]:
                        g_best = deepcopy(current_best)
                g_best_list.append(g_best[self.ID_FIT])
                time_epoch_end = time() - time_epoch_start
                print(f'Current best fit {current_best[self.ID_FIT]:.4f}, '
                      f'Global best fit {g_best[self.ID_FIT]:.4f}, '
                      f'Epoch {epoch + 1} with time: {time_epoch_end:.2f}')
                if time() - time_bound_start >= self.time_bound:
                    print('====== Over time for training ======')
                    break
            return g_best[0], g_best[1], array(g_best_list)

