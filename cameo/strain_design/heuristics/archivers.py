# Copyright 2014 Novo Nordisk Foundation Center for Biosustainability, DTU.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from bisect import insort, bisect
import inspyred


class BestSolutionArchiver(object):

    def __init__(self):
        self.worst_fitness = None
        self.archive = []

    def __name__(self):
        return "BestSolutionArchiver"

    def __call__(self, random, population, archive, args):
        self.archive = archive
        size = args.get('max_archive_size', 100)
        [self.add(individual.candidate, individual.fitness, size) for individual in population]
        return self.archive

    def add(self, candidate, fitness, max_size):
        if self.worst_fitness is None:
            self.worst_fitness = fitness

        if fitness >= self.worst_fitness:

            candidate = SolutionTuple(candidate, fitness)
            add = True
            for c in self.archive:
                if candidate.improves(c) and candidate.fitness == c.fitness:
                    self.archive.remove(c)
                if c.improves(candidate) and candidate.fitness == c.fitness:
                    add = False

            if add:
                insort(self.archive, candidate)

            while len(self.archive) > max_size:
                self.archive.pop()

            self.worst_fitness = self.archive[len(self.archive) - 1].fitness

    def length(self):
        return len(self.archive)

    def get(self, index):
        return self.archive[index]

    def __iter__(self):
        for solution in self.archive:
            yield solution


class SolutionTuple(object):
        def __init__(self, candidate, fitness):
            self.candidate = set(candidate)
            self.fitness = fitness

        def __eq__(self, other):
            return self.candidate == other.candidate and self.fitness == other.fitness

        def __cmp__(self, other):
            if self.fitness > other.fitness:
                return -1
            elif self.fitness == other.fitness:
                if self.improves(other):
                    return -1
                elif self == other:
                    return 0
                else:
                    return 1
            else:
                return 1

        def __str__(self):
            return "%s - %s" % (list(self.candidate), self.fitness)

        def __repr__(self):
            return "SolutionTuple #%s: %s" % (id(self), self.__str__())

        def issubset(self, other):
            return self.candidate.issubset(other.candidate)

        def symmetric_difference(self, other):
            return self.candidate.symmetric_difference(other.candidate)

        def improves(self, other):
            assert isinstance(other, SolutionTuple)
            return self.issubset(other) and len(self.symmetric_difference(other)) > 0 and self.fitness >= other.fitness