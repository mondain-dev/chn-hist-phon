import os
import csv

import pandas as pd
import numpy as np
import scipy

from fancyimpute import SoftImpute
from sklearn.decomposition import DictionaryLearning, SparseCoder

# configuration
DIR_DATA= '/path/to/ChnHistPhon/results'

# parameters
n_rank = 200
n_components = 300

# Loading Data
X = np.genfromtxt(os.path.join(DIR_DATA, 'ChnCharData.csv'), delimiter=',', skip_header=True)
with open(os.path.join(DIR_DATA, 'ChnCharData.csv'), 'r') as f:
    csv_reader = csv.reader(f)
    features = [s.decode('utf-8') for s in next(csv_reader)]

char_list = pd.read_csv(os.path.join(DIR_DATA, 'ChnChar.csv'))

# run soft-impute
idx_nan  = np.where(np.isnan(X))
idx_mask = np.where(~np.isnan(X))
Z = SoftImpute().fit_transform(X)

# run sparse dictionary learning 
dictionary_learning = DictionaryLearning(n_components=n_components, max_iter=100, verbose=2)
X_fit = dictionary_learning.fit(Z)
dictionary = X_fit.components_
sparse_coder = SparseCoder(dictionary)
code = sparse_coder.transform(Z)

X_recon = code.dot(dictionary)
e = ((X_recon[idx_mask] - X[idx_mask]) ** 2).sum()/(X[idx_mask] ** 2).sum()
print("Reconstruction error: %.2f%%" % (e*100))

with open(os.path.join(DIR_DATA, 'dictionary.csv'), 'w') as f:
    csv_writer = csv.writer(f, delimiter=',')
    csv_writer.writerow([f.encode('utf-8') for f in features])
    for r in dictionary:
        csv_writer.writerow(r)

with open(os.path.join(DIR_DATA, 'code.csv'), 'w') as f:
    csv_writer = csv.writer(f, delimiter=',')
    csv_writer.writerow(['entry_%d' % entry for entry in range(n_components)])
    for r in code:
        csv_writer.writerow(r)
