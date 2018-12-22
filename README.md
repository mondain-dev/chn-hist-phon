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
We used `softImpute` to perform low-rank SVD on sparse data matrix from `ChnCharData.csv` with missing value imputation, which is implemented in `ChnHistPhon_2_run_softImpute.R`.
 
## Results
Here we show some results of SVD on the `ChnCharData.csv`. 

The first few components corresponding to the largest singular values appear to explain, primarily, the tone features. Characters with highest scores (absolute value) on the component corresponding to the largest singular value:

| 伊 | 夜 | 儀 | 枷 | 鵝 | 娥 | ... |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| -0.01503999 | -0.01503295 | -0.01486257 | -0.01483582 | -0.01473751 | -0.01473751 ... |

with phonetic features:

| Feature  | loading |
| ------------- | ------------- |
| pinyin_tone.4  |  -0.3473871 |
| yyef_jyutping_cod.ZERO  | -0.3280398 |
| pinyin_tone.2 | -0.2474036 |
| ja_on_cod.ZERO| -0.2448645 |
| kr_cod.ZERO | -0.1999326 |
| pinyin_tone.1 | -0.1982626 |
| ... | ... |

Characters with highest scores (absolute value) on the component corresponding to the 2nd largest singular value:

| 鑼 | 羅 | 鱸 | 廊 | 搖 | 蹉 | ... |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| -0.01585882 | -0.01545246 | -0.01495460 | -0.01490540 | -0.01464938 | -0.01463729 | ... |

with phonetic features:

| Feature  | loading |
| ------------- | ------------- |
| pinyin_tone.4  |  0.7505250 |
| pinyin_tone.2  | -0.1951117 |
| yyef_jyutping_ton.6 | 0.1818968 |
| yyef_jyutping_ton.4 | -0.1502338 |
| pinyin_tone.1 | -0.1470119 |
| ja_on_cod.ZERO | -0.1356398 |
| ... | ... |

Corresponding to the 6th largest singular value, we have the following component which explains the -n ending:

| 婉 | 引 | 偃 | 譴 | 緊 | 菫 | ... |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| -0.02874410 | -0.02850587 | -0.02746337 | -0.02726452 | -0.02680066 | -0.02673988 | ... |

with phonetic features:

| Feature  | loading |
| ------------- | ------------- |
| pinyin_tone.3  |  -0.5239291 |
| yyef_jyutping_cod.n | -0.2928186 |
| ja_on_cod.N | -0.2185322 |
| kr_cod.N | -0.2158316 |
| yyef_jyutping_ton.2 | -0.2014447 |
| pinyin_onset.ZERO | -0.1955354 |
| ... | ... |

The 10th largest singular value appears to relate to the consonants:

| 止 | 旨 | 紙 | 芷 | 値 | 姉 | 䤠 | 高 | 指| 扺 | 齒 | 豕| 膏 | 肝 | 官 | 棺 | 痔 | 拭 | ... |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| -0.0291 | -0.0291 | -0.0291 | -0.0291 | -0.0263 | -0.0263 |  -0.0262 | 0.0260 |  -0.0258 | -0.0255 | -0.0253 |  -0.0251 | 0.0251 | 0.0247 | 0.0247 | 0.0245 | -0.0244 | -0.0242 | ... |

with phonetic features:

| Feature  | loading |
| ------------- | ------------- |
| yyef_jyutping_nuc.i | -0.3029058 |
| ja_on_ons.K  | 0.2829328 |
| kr_ons.K | 0.2360833 |
| yyef_jyutping_ons.z | -0.2157885  |
| vi_cod_north.ZERO | -0.1815387 |
| vi_cod_central.ZERO | -0.1815387 |
| ... | ... |
