# import torch
#
#
# def parallel_db(db, i):
#     return torch.cat([db[:i], db[i + 1:]])
#
#
# def parallel_dbs(db):
#     list_dbs = []
#     for i in range(len(db)):
#         new_dbs = parallel_db(db, i)
#         list_dbs.append(new_dbs)
#     return list_dbs
#
#
# def create_list_parallel_databases(num_entries):
#     db = torch.rand(num_entries) > 0.5
#     pdbs = parallel_dbs(db)
#     return db, pdbs
#
#
# def query(db, threshold=5):
#     return (db.sum() > threshold).float()
#
# def sensitivity(query, num_entries=10):
#     db, pdbs = create_list_parallel_databases(num_entries) #NB.function creating input database from which the parallel dbs are generated MUST be included inside the sensitivity function
#     query_db = query(db)
#     max_distance=0
#     for pdb in pdbs:
#         query_pdb = query(pdb)
#         db_distance=torch.abs(query_pdb - query_db)
#         if (db_distance > max_distance):
#             max_distance=db_distance
#     return max_distance