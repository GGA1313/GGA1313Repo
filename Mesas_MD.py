#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import dimod
from typing import Sequence
from dwave.system import LeapHybridCQMSampler

def AssignSeats ():
    
    total_num_tables = 16
    num_tables_dinning_room = 8
    num_persons = 32
    table_capacity = 4

    cod_persons = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "31",
        "32",
    ]



    num_tables_first_meal = int(total_num_tables / num_tables_dinning_room)
    tables_first_meal = range(num_tables_first_meal)
    # last_table_second_meal = int (num_tables_first_meal * 2)
    tables_second_meal = range (num_tables_first_meal, total_num_tables)

    cqm = dimod.ConstrainedQuadraticModel ()

    seats = {}

    for t in range (total_num_tables):
        for p in range (num_persons):
            # each table - person pair is a binary variable
            pair = dimod.Binary (
	            f" table_{t}_person_{p}"
	        )
            seats [t, p] = pair

    # Each table has limited capacity
    for t in range (total_num_tables):
        cqm.add_constraint_from_comparison (
            dimod.quicksum (
                seats [t, p] for p in range (num_persons)
            ) <= table_capacity
        )
        
    # For every meal, everybody seats at one table
    for p in range (num_persons):
        cqm.add_constraint_from_comparison (
            dimod.quicksum (
                seats [t, p] for t in tables_first_meal
            ) == 1
        )
        
    for p in range (num_persons):
        cqm.add_constraint_from_comparison (
            dimod.quicksum (
                seats [t, p] for t in tables_second_meal
            ) == 1
        )
        

    same_table = {}

    for p1 in range (num_persons - 1):
        for p2 in range (p1+1, num_persons):
            for t in range (total_num_tables):
            # each triplet peson1, person2, table is a binary variable
                triplet = dimod.Binary (
                    f" person1_{p1}_seats_with_person2_{p2}_at_table_{t}"
                )
                same_table [p1, p2, t] = triplet


    # Any two people can only seat once at the same table.

    for p1 in range (num_persons - 1):
        for p2 in range (p1+1, num_persons):
            cqm.add_constraint_from_comparison (
                dimod.quicksum (
                    same_table [p1, p2, t] for t in range (total_num_tables)
                ) <= 1
            )




    # maximize the total value of deal mix per customer offered deals
    # 17/12/2023. Lo siguiente da un error. Hay que ver cómo escribirlo para que no 
    # haya un quicksum dentro de otro.

    # colocate = {}

    # colocate[p1][p2] = dimod.quicksum(same_table[p1, p2, t] for p1 in range (num_persons - 1) for p2 in range (p1+1, num_persons) for t in range (total_num_tables))

    """cqm.set_objective (
        dimod.quicksum (
            connections[p1][p2] * same_table[p1, p2, t]
            for p1 in range(num_persons - 1)
            for p2 in range(p1 + 1, num_persons)
            for t in range(total_num_tables)
            if connections[p1][p2] > 0
        ),
    )"""

    colocate = {}

    for p1 in range (num_persons - 1):
        for p2 in range (p1+1, num_persons):
            colocate[p1, p2] = dimod.quicksum(same_table[p1, p2, t] for t in range (total_num_tables))


    cqm.set_objective (
        dimod.quicksum (
            colocate[p1, p2]
            for p1 in range(num_persons - 1)
            for p2 in range(p1 + 1, num_persons)
        ),
    )

    

    sampler = LeapHybridCQMSampler()     



    sampleset = sampler.sample_cqm(cqm,
                               time_limit=180,
                               label="MD seats allocation")  
                               
    feasible_sampleset = sampleset.filter(lambda row: row.is_feasible)  
    
    if len(feasible_sampleset):      
       best = feasible_sampleset.first
       print("{} feasible solutions of {}.".format(
          len(feasible_sampleset), len(sampleset)))
      

    # selected_bins = [key for key, val in best.sample.items() if 'bin_used' in key and val]   
    # print("{} bins are used.".format(len(selected_bins)))


    
    
def main(argv: Sequence[str]) -> None:
    #if len(argv) > 1:
    #    raise app.UsageError("Too many command-line arguments.")
    AssignSeats()


if __name__ == "__main__":
    #app.run(main)
    main("")
