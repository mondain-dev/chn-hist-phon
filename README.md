# ChnHistPhon - Chinese Historical Phonology

Experiments in Chinese Historical Phonology using matrix decomposition and factorization methods.

## Prerequisites
We use python for to prepare our data. The following packages are required:
 - pandas
 - numpy
 - [cjklib](https://pypi.org/project/cjklib/)
 - [vPhon: a Vietnamese phonetizer](https://github.com/kirbyj/vPhon): clone it to your local directory `/path/to/vPhon`
 - [fancyimpute](https://github.com/iskandr/fancyimpute): install it from github repository

In addition to [cjklib](https://pypi.org/project/cjklib/), [Unihan Database](http://unicode.org/charts/unihan.html) is used. The latest `Unihan.zip` can be downloaded from https://www.unicode.org/Public/UCD/. Unzip it to `/path/to/Unihan`.
 
## Running experiments
### Prepare data 
Once you have cloned this repository to your local `/path/to/ChnHistPhon`, you can run
```
python /path/to/ChnHistPhon/ChnHistPhon_1_data_preparation.py
```
which will create `ChnCharData.csv` a dataset of Chinese characters we need in `/path/to/ChnHistPhon/results`.
### Perform low-rank SVD
We used `softImpute` ([Mazumder et al., 2010.](http://www.jmlr.org/papers/v11/mazumder10a.html) to complete the data matrix in `ChnCharData.csv`, which is followed by dictionary learning and sparse coding in `ChnHistPhon_2_run_SoftImpute_DictionaryLearning.py`.
 
## Results
The results can be viewed [here](https://chinese-historical-phonology.herokuapp.com/).
