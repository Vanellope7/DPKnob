import pandas as pd
import torch


def parallel_db(db, i):
    return db.drop(i)



def parallel_dbs(db):
    list_dbs = []
    for i in range(len(db)):
        new_dbs = parallel_db(db, i)
        list_dbs.append(new_dbs)
    return list_dbs

def query(db, threshold=5):
    return db.sum()

def sensitivity(db, pdbs, query):
    query_db = query(db)
    max_distance = 0
    for pdb in pdbs:

        query_pdb = query(pdb)
        db_distance = abs(query_pdb - query_db)
        if (db_distance > max_distance):
            max_distance=db_distance
    return max_distance

df = pd.read_csv('../data/animals_and_carrots.csv', sep=",")
db = df['carrots_eaten']
print(sensitivity(db, parallel_dbs(db), query))
# print(parallel_dbs(df['carrots_eaten']))
# print(query(df['carrots_eaten']))
# print(db['carrots_eaten'])
# print(parallel_db(db['carrots_eaten'], 1))