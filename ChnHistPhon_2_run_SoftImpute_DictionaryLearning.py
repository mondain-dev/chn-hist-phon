import os
import csv

import pandas as pd
import numpy as np
import scipy

from fancyimpute import SoftImpute
from sklearn.decomposition import TruncatedSVD, DictionaryLearning, SparseCoder

from sqlalchemy import create_engine

# configuration
DIR_DATA= '/path/to/ChnHistPhon/results'
con = create_engine('postgresql://@localhost:5432/chp_db')

# parameters
n_rank = 200
n_entries = 200

# Loading Data
ChnCharData = pd.read_csv(os.path.join(DIR_DATA, 'ChnCharData.csv'))
X = ChnCharData.values
with open(os.path.join(DIR_DATA, 'ChnCharData.csv'), 'r') as f:
    csv_reader = csv.reader(f)
    features = [s.decode('utf-8') for s in next(csv_reader)]

char_list = pd.read_csv(os.path.join(DIR_DATA, 'ChnChar.csv'))

# run soft-impute
idx_nan  = np.where(np.isnan(X))
idx_mask = np.where(~np.isnan(X))
Z = SoftImpute(max_rank = n_rank, max_iters = 250).fit_transform(X)

svd = TruncatedSVD(n_rank) 
svd.fit(Z)
X_imputed = svd.transform(Z).dot(svd.components_)
e = ((X_imputed[idx_mask] - X[idx_mask]) ** 2).sum()/(X[idx_mask] ** 2).sum()
print("Imputation error: %.2f%%" % (e*100))

# run sparse dictionary learning
dictionary_learning = DictionaryLearning(n_components = n_entries, max_iter = 150, transform_algorithm = "lasso_lars", positive_code=True, verbose = 2)
dictionary_learning.fit(Z)
dictionary = dictionary_learning.components_
code = dictionary_learning.transform(Z)

X_recon = code.dot(dictionary)
e = ((X_recon[idx_mask] - X[idx_mask]) ** 2).sum()/(X[idx_mask] ** 2).sum()
print("Reconstruction error: %.2f%%" % (e*100))

char_code = pd.DataFrame(code, columns = ['entry_' + str(i+1) for i in range(code.shape[1])])
char_code = pd.concat([pd.read_csv(os.path.join(DIR_DATA, 'ChnChar.csv')), char_code], axis=1)

dictionary = pd.DataFrame(dictionary_learning.components_, columns = ['feature_' + str(i+1) for i in range(X.shape[1])])
dictionary['entry'] = ['entry_' + str(i+1) for i in range(dictionary.shape[0])]

feature_name = pd.DataFrame.from_dict({'feature_id': ['feature_' + str(i+1) for i in range(ChnCharData.shape[1])], 'feature': ChnCharData.columns.tolist()})

# write to database
char_code.to_sql('char_code', con, if_exists='replace', index=False)
dictionary.to_sql('dictionary', con, if_exists='replace', index=False)
feature_name.to_sql('feature_name', con, if_exists='replace', index=False)

# write to csv
char_code.to_csv(os.path.join(DIR_DATA, 'char_code.csv'), index=False)
dictionary.to_csv(os.path.join(DIR_DATA, 'dictionary.csv'), index=False)
feature_name.to_csv(os.path.join(DIR_DATA, 'feature_name.csv'), index=False)
