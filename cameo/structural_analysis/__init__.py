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
from itertools import combinations
from ordered_set import OrderedSet

N = "-"


def identify_currency_metabolites_by_pattern(model, matrix=None, top_ranked=20, min_combination=3, max_combination=5):
    if matrix is None:
        matrix = model.S

    metabolites_degree = dict([[m.id, len(m.reactions)] for m in model.metabolites])
    metabolites = metabolites_degree.keys()
    metabolites = sorted(metabolites, key=metabolites_degree.get)
    metabolites.reverse()
    top_hits = metabolites[:top_ranked]

    possible_motifs = {}

    for i in xrange(min_combination, max_combination):
        for motif in combinations(top_hits, i):
            key = frozenset(OrderedSet(motif))
            possible_motifs[key] = 0

    for i, reaction in enumerate(model.reactions):
        print reaction
        seq = list(top_hits)
        count = 0
        for j, met in enumerate(reaction.metabolites.keys()):
            coeff = matrix.get(i, j)
            try:
                index = seq.index(met)

                if met in top_hits and coeff != 0:
                    seq[index] = met
                    count += 1
                else:
                    seq[index] = N
            except ValueError:
                pass
        sequence_motifs = []
        seq = set(seq)

        for motif in possible_motifs.keys():
            if motif.issubset(seq):
                add = True
                for other_motif in sequence_motifs:
                    if motif.issubset(other_motif):
                        add = False
                    if other_motif.issubset(motif):
                        sequence_motifs.remove(other_motif)

                if add:
                    sequence_motifs.append(motif)

        print "seq motifs: ", sequence_motifs
        for motif in sequence_motifs:
            possible_motifs[motif] += 1

        motifs = possible_motifs.keys()
        motifs = sorted(motifs, key=possible_motifs.get)
        motifs.reverse()
        for m in motifs[:5]:
            print m, ": ", possible_motifs[m]

    return possible_motifs