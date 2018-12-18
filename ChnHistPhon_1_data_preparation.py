import os, sys, inspect
import re
import csv

import numpy as np
import pandas as pd

from cjklib import characterlookup
from cjklib.reading import operator

# configuring
DIR_WORKING='/path/to/ChnHistPhon'
DIR_Unihan='/path/to/Unihan'
DIR_vPhon='/path/to/vPhon'
sys.path.append(DIR_vPhon)
sys.path.append(os.path.join(DIR_vPhon, 'Rules'))
import vPhon

Unihan_Readings_txt = os.path.join(DIR_Unihan, 'Unihan_Readings.txt')
Unihan_Readings = pd.read_csv(Unihan_Readings_txt, sep='\t' , lineterminator='\n', comment="#", header=None, encoding='utf-8', names=['code', 'field', 'value'], keep_default_na=False)
Unihan_Readings_kMandarin = Unihan_Readings.query('field == "kMandarin"').sort_values(by=['code'])
Unihan_Readings_kKorean = Unihan_Readings.query('field == "kKorean"').sort_values(by=['code'])
Unihan_Readings_kJapaneseOn = Unihan_Readings.query('field == "kJapaneseOn"').sort_values(by=['code'])
Unihan_Readings_kVietnamese = Unihan_Readings.query('field == "kVietnamese"').sort_values(by=['code'])
Unihan_Readings_kCantonese = Unihan_Readings.query('field == "kCantonese"').sort_values(by=['code'])

Unihan_Variants_txt = os.path.join(DIR_Unihan, 'Unihan_Variants.txt')
Unihan_Variants = pd.read_csv(Unihan_Variants_txt, sep='\t' , lineterminator='\n', comment="#", header=None, encoding='utf-8', names=['code', 'field', 'value'], keep_default_na=False)
Unihan_Variants_kTraditionalVariant = Unihan_Variants.query('field == "kTraditionalVariant"').sort_values(by=['code'])

def queryPinyin(code_point_str):
  unicode_char = unichr(int(code_point_str.replace("U+", ""),16))
  pinyin = dict([])
  ## query cjklib
  cjk = characterlookup.CharacterLookup('C')
  pinyin_cjklib = ''
  try:
    pinyin_cjklib = cjk.getReadingForCharacter(unicode_char, 'Pinyin')
  except:
    print "cjklib error: getting Pinyin for: " + unicode_char
    pass
  pyOp = operator.PinyinOperator()
  if pinyin_cjklib:
    if 'r' in pinyin_cjklib:
      pinyin_cjklib[pinyin_cjklib.index('r')] = u'er'
    py_syllable_tone = [list(pyOp.splitEntityTone(x)) for x in pinyin_cjklib]
    py_syllable = [x[0] for x in py_syllable_tone]
    py_tone     = [x[1] for x in py_syllable_tone]

    py_onset_rhyme = [list(pyOp.getOnsetRhyme(x)) for x in py_syllable]
    py_onset       = [x[0] for x in py_onset_rhyme]
    py_rhyme       = [x[1] for x in py_onset_rhyme]

    pinyin['pinyin_onset'] = py_onset
    pinyin['pinyin_rhyme'] = py_rhyme
    pinyin['pinyin_tone'] = py_tone

  ## query Unihan Readings data
  il = Unihan_Readings_kMandarin['code'].searchsorted(code_point_str, 'left')[0]
  ir = Unihan_Readings_kMandarin['code'].searchsorted(code_point_str, 'right')[0]
  df = Unihan_Readings_kMandarin.iloc[il:ir,:]
  pinyin_unihan = [v for r in df.itertuples() for v in r.value.split()]
  if pinyin_unihan:
      py_syllable_tone = [list(pyOp.splitEntityTone(x)) for x in pinyin_unihan]
      py_syllable = [x[0] for x in py_syllable_tone]
      py_tone     = [x[1] for x in py_syllable_tone]

      py_onset_rhyme = ()
      try:
        py_onset_rhyme = [list(pyOp.getOnsetRhyme(x)) for x in py_syllable]
      except:
        print "Unihan Readings error: getting Pinyin for: " + unicode_char + " " + ' '.join(pinyin_unihan)
        pass
      if py_onset_rhyme:
        py_onset       = [x[0] for x in py_onset_rhyme]
        py_rhyme       = [x[1] for x in py_onset_rhyme]

        if pinyin:
          pinyin['pinyin_onset'].extend(py_onset)
          pinyin['pinyin_rhyme'].extend(py_rhyme)
          pinyin['pinyin_tone'].extend(py_tone)
        else:
          pinyin['pinyin_onset'] = py_onset
          pinyin['pinyin_rhyme'] = py_rhyme
          pinyin['pinyin_tone'] = py_tone

  return pinyin

def parseJapaneseOn(ja_on_str):
  ja_on_ons = re.findall("^B|^CH|^D|^F|^G|^H|^J|^K|^R|^M|^N|^SH*|^T|^W|^Y|^Z|^", ja_on_str)[0]
  ja_on_cod = re.findall("KU$|N$|CHI$|TSU$|KI$|$", ja_on_str)[0]
  ja_on_nuc = re.sub("^B|^CH|^D|^F|^G|^H|^J|^K|^R|^M|^N|^SH*|^T|^W|^Y|^Z|^", "", ja_on_str)
  ja_on_nuc = re.sub("KU$|N$|CHI$|TSU$|KI$|$", "", ja_on_nuc)
  return (ja_on_ons, ja_on_nuc, ja_on_cod)

def queryJapaneseOnUnihanReadings(code_point_str):
  unicode_char = unichr(int(code_point_str.replace("U+", ""),16))
  ja_on = dict([])
  ## query Unihan Readings data
  il = Unihan_Readings_kJapaneseOn['code'].searchsorted(code_point_str, 'left')[0]
  ir = Unihan_Readings_kJapaneseOn['code'].searchsorted(code_point_str, 'right')[0]
  df = Unihan_Readings_kJapaneseOn.iloc[il:ir,:]
  ja_on_unihan = [v for r in df.itertuples() for v in r.value.split()]
  if ja_on_unihan:
      ja_on_parsed = [parseJapaneseOn(x) for x in ja_on_unihan]
      ja_on['on_ons'] = [x[0] for x in ja_on_parsed]
      ja_on['on_nuc'] = [x[1] for x in ja_on_parsed]
      ja_on['on_cod'] = [x[2] for x in ja_on_parsed]
  return ja_on

def parseKoreanUnihan(kr_str):
  kr_ons = re.findall("^CH*|^H|^K[HK]*|^L|^M|^N|^P[PH]*|^SS*|^TH*|^W|^Y|^", kr_str)[0]
  kr_cod = re.findall("NG*$|K$|L$|M$|P$|S$|C$|T$|$", kr_str)[0]
  kr_nuc = re.sub("^CH*|^H|^K[HK]*|^L|^M|^N|^P[PH]*|^SS*|^TH*|^W|^Y|^", "", kr_str)
  kr_nuc = re.sub("NG*$|K$|L$|M$|P$|S$|C$|T$|$", "", kr_nuc)
  return (kr_ons, kr_nuc, kr_cod)

def queryKoreanUnihanReadings(code_point_str):
  unicode_char = unichr(int(code_point_str.replace("U+", ""),16))
  kr = dict([])
  ## query Unihan Readings data
  il = Unihan_Readings_kKorean['code'].searchsorted(code_point_str, 'left')[0]
  ir = Unihan_Readings_kKorean['code'].searchsorted(code_point_str, 'right')[0]
  df = Unihan_Readings_kKorean.iloc[il:ir,:]
  kr_unihan = [v for r in df.itertuples() for v in r.value.split()]
  if kr_unihan:
      kr_parsed = [parseKoreanUnihan(x) for x in kr_unihan]
      kr['kr_ons'] = [x[0] for x in kr_parsed]
      kr['kr_nuc'] = [x[1] for x in kr_parsed]
      kr['kr_cod'] = [x[2] for x in kr_parsed]
  return kr

def queryVietnameseUnihanReadings(code_point_str):
  unicode_char = unichr(int(code_point_str.replace("U+", ""),16))
  vi = dict([])
  ## query Unihan Readings data
  il = Unihan_Readings_kVietnamese['code'].searchsorted(code_point_str, 'left')[0]
  ir = Unihan_Readings_kVietnamese['code'].searchsorted(code_point_str, 'right')[0]
  df = Unihan_Readings_kVietnamese.iloc[il:ir,:]
  vi_unihan = [v for r in df.itertuples() for v in r.value.split()]
  if vi_unihan:
      vi_north_parsed   = [vPhon.trans(w.lower(), 'n', 0,0,0,0) for w in vi_unihan]
      vi_central_parsed = [vPhon.trans(w.lower(), 'c', 0,0,0,0) for w in vi_unihan]
      vi_south_parsed   = [vPhon.trans(w.lower(), 's', 0,0,0,0) for w in vi_unihan]
      vi['vi_ons_north'] = [x[0] for x in vi_north_parsed]
      vi['vi_ons_central'] = [x[0] for x in vi_central_parsed]
      vi['vi_ons_south'] = [x[0] for x in vi_south_parsed]
      vi['vi_nuc_north'] = [x[1] for x in vi_north_parsed]
      vi['vi_nuc_central'] = [x[1] for x in vi_central_parsed]
      vi['vi_nuc_south'] = [x[1] for x in vi_south_parsed]
      vi['vi_cod_north'] = [x[2] for x in vi_north_parsed]
      vi['vi_cod_central'] = [x[2] for x in vi_central_parsed]
      vi['vi_cod_south'] = [x[2] for x in vi_south_parsed]
      vi['vi_ton_north'] = [x[3] for x in vi_north_parsed]
      vi['vi_ton_central'] = [x[3] for x in vi_central_parsed]
      vi['vi_ton_south'] = [x[3] for x in vi_south_parsed]
  return vi

def parseJyutping(jyutping_str):
  jyutping_syl = re.sub("[0-9]*$","", jyutping_str)
  jyutping_ton = re.findall("[0-9]*$", jyutping_str)[0]
  jyutping_ons = re.findall("^b|^c|^d|^f|^gw*|^h|^kw*|^j|^l|^m|^ng*|^p|^s|^t|^w|^z|^", jyutping_syl)[0]
  jyutping_cod = re.findall("ng*$|m$|k$|p$|t$|$", jyutping_syl)[0]
  jyutping_nuc = re.sub("^b|^c|^d|^f|^gw*|^h|^kw*|^j|^l|^m|^ng*|^p|^s|^t|^w|^z|^", "", jyutping_syl)
  jyutping_nuc = re.sub("ng*$|m$|k$|p$|t$|$", "", jyutping_nuc)
  return (jyutping_ons, jyutping_nuc, jyutping_cod, jyutping_ton)

def queryCantoneseUnihanReadings(code_point_str):
  unicode_char = unichr(int(code_point_str.replace("U+", ""),16))
  yyef_jyutping = dict([])
  ## query Unihan Readings data
  il = Unihan_Readings_kCantonese['code'].searchsorted(code_point_str, 'left')[0]
  ir = Unihan_Readings_kCantonese['code'].searchsorted(code_point_str, 'right')[0]
  df = Unihan_Readings_kCantonese.iloc[il:ir,:]
  yyef_jyutping_unihan  = [v for r in df.itertuples() for v in r.value.split()]
  if yyef_jyutping_unihan:
      yyef_jyutping_parsed = [parseJyutping(x) for x in yyef_jyutping_unihan]
      yyef_jyutping['yyef_jyutping_ons'] = [x[0] for x in yyef_jyutping_parsed]
      yyef_jyutping['yyef_jyutping_nuc'] = [x[1] for x in yyef_jyutping_parsed]
      yyef_jyutping['yyef_jyutping_cod'] = [x[2] for x in yyef_jyutping_parsed]
      yyef_jyutping['yyef_jyutping_ton'] = [x[3] for x in yyef_jyutping_parsed]
  return yyef_jyutping

def queryShanghaineseCJKLIB(code_point_str):
  unicode_char = unichr(int(code_point_str.replace("U+", ""),16))
  sh_IPA = dict([])
  ## query cjklib
  cjk = characterlookup.CharacterLookup('C')
  sh_IPA_cjklib = cjk.getReadingForCharacter(unicode_char, 'ShanghaineseIPA')
  if sh_IPA_cjklib:
    shIPAOp = operator.ShanghaineseIPAOperator()
    sh_IPA_syllable_tone = [list(shIPAOp.splitEntityTone(x)) for x in sh_IPA_cjklib]
    sh_IPA_syllable = [x[0] for x in sh_IPA_syllable_tone]
    sh_IPA_tone     = [x[1] for x in sh_IPA_syllable_tone]

    sh_IPA_onset_rhyme = [list(shIPAOp.getOnsetRhyme(x)) for x in sh_IPA_syllable]
    sh_IPA_onset       = [x[0] for x in sh_IPA_onset_rhyme]
    sh_IPA_rhyme       = [x[1] for x in sh_IPA_onset_rhyme]

    sh_IPA['sh_IPA_onset'] = sh_IPA_onset
    sh_IPA['sh_IPA_rhyme'] = sh_IPA_rhyme
    sh_IPA['sh_IPA_tone']  = sh_IPA_tone

  return sh_IPA

def getTraditionalVariant(code_point_str):
    il = Unihan_Variants_kTraditionalVariant['code'].searchsorted(code_point_str, 'left')[0]
    ir = Unihan_Variants_kTraditionalVariant['code'].searchsorted(code_point_str, 'right')[0]
    df = Unihan_Variants_kTraditionalVariant.iloc[il:ir,:]
    t_variant = [v for r in df.itertuples() for v in r.value.split()]
    if len(t_variant) == 0:
        t_variant.append(code_point_str)
    return t_variant

def featureStringVectorizer(feature_str_list, feature_name="feature"):
  sample_size = len(feature_str_list)
  vocab = list(set().union(*feature_str_list))
  vocab_size = len(vocab)
  v = np.zeros((sample_size, vocab_size))
  v_availability = np.zeros(sample_size)

  for i in range(sample_size):
    if feature_str_list[i]:
      v[i, [vocab.index(x) for x in feature_str_list[i]]] += (1.0/len(feature_str_list[i]))
      v_availability[i] = 1
    else:
      v[i] = None

  v_names = ['.'.join([feature_name, x if isinstance(x, basestring) else str(x)]) if x else '.'.join([feature_name, 'ZERO']) for x in vocab]

  return (v, v_availability, v_names)

# list of characters
print("Generating character list ... ")
char_list = list(set(list(Unihan_Readings.code)))
t_char_list = [tc for c in char_list for tc in getTraditionalVariant(c)]
t_char_list = list(set(t_char_list))
print("done.")

print("Reading Japanese On data ... ")
ja_on_list  = [queryJapaneseOnUnihanReadings(c) for c in t_char_list]
print("done.")

print("Reading Korean data ... ")
kr_list     = [queryKoreanUnihanReadings(c) for c in t_char_list]
print("done.")

print("Reading Vietnamese data ... ")
vi_list     = [queryVietnameseUnihanReadings(c) for c in t_char_list]
print("done.")

print("Reading Cantonese data ... ")
yyef_jyutping_list = [queryCantoneseUnihanReadings(c) for c in t_char_list]
print("done.")

print("Reading Shanghainese data ... ")
sh_IPA_list = [queryShanghaineseCJKLIB(c) for c in t_char_list]
print("done.")

print("Reading Pinyin data ... ")
pinyin_list = [queryPinyin(c) for c in t_char_list]
print("done.")

ja_on_ons_str_list = [x['on_ons'] if x else [] for x in ja_on_list ]
ja_on_nuc_str_list = [x['on_nuc'] if x else [] for x in ja_on_list ]
ja_on_cod_str_list = [x['on_cod'] if x else [] for x in ja_on_list ]

kr_ons_str_list = [x['kr_ons'] if x else [] for x in kr_list ]
kr_nuc_str_list = [x['kr_nuc'] if x else [] for x in kr_list ]
kr_cod_str_list = [x['kr_cod'] if x else [] for x in kr_list ]

vi_ons_north_str_list = [x['vi_ons_north'] if x else [] for x in vi_list]
vi_nuc_north_str_list = [x['vi_nuc_north'] if x else [] for x in vi_list]
vi_cod_north_str_list = [x['vi_cod_north'] if x else [] for x in vi_list]
vi_ton_north_str_list = [x['vi_ton_north'] if x else [] for x in vi_list]
vi_ons_central_str_list = [x['vi_ons_central'] if x else [] for x in vi_list]
vi_nuc_central_str_list = [x['vi_nuc_central'] if x else [] for x in vi_list]
vi_cod_central_str_list = [x['vi_cod_central'] if x else [] for x in vi_list]
vi_ton_central_str_list = [x['vi_ton_central'] if x else [] for x in vi_list]
vi_ons_south_str_list = [x['vi_ons_south'] if x else [] for x in vi_list]
vi_nuc_south_str_list = [x['vi_nuc_south'] if x else [] for x in vi_list]
vi_cod_south_str_list = [x['vi_cod_south'] if x else [] for x in vi_list]
vi_ton_south_str_list = [x['vi_ton_south'] if x else [] for x in vi_list]

yyef_jyutping_ons_str_list = [x['yyef_jyutping_ons'] if x else [] for x in yyef_jyutping_list]
yyef_jyutping_nuc_str_list = [x['yyef_jyutping_nuc'] if x else [] for x in yyef_jyutping_list]
yyef_jyutping_cod_str_list = [x['yyef_jyutping_cod'] if x else [] for x in yyef_jyutping_list]
yyef_jyutping_ton_str_list = [x['yyef_jyutping_ton'] if x else [] for x in yyef_jyutping_list]

sh_IPA_onset_str_list = [x['sh_IPA_onset'] if x else [] for x in sh_IPA_list]
sh_IPA_rhyme_str_list = [x['sh_IPA_rhyme'] if x else [] for x in sh_IPA_list]
sh_IPA_tone_str_list  = [x['sh_IPA_tone'] if x else [] for x in sh_IPA_list]

pinyin_onset_str_list = [x['pinyin_onset'] if x else [] for x in pinyin_list]
pinyin_rhyme_str_list = [x['pinyin_rhyme'] if x else [] for x in pinyin_list]
pinyin_tone_str_list  = [x['pinyin_tone'] if x else [] for x in pinyin_list]

# Vectorise
X_ja_on_ons, ja_on_ons_availability, ja_on_ons_names = featureStringVectorizer(ja_on_ons_str_list, 'ja_on_ons')
X_ja_on_nuc, ja_on_nuc_availability, ja_on_nuc_names = featureStringVectorizer(ja_on_nuc_str_list, 'ja_on_nuc')
X_ja_on_cod, ja_on_cod_availability, ja_on_cod_names = featureStringVectorizer(ja_on_cod_str_list, 'ja_on_cod')

X_kr_ons, kr_ons_availability, kr_ons_names = featureStringVectorizer(kr_ons_str_list, 'kr_ons')
X_kr_nuc, kr_nuc_availability, kr_nuc_names = featureStringVectorizer(kr_nuc_str_list, 'kr_nuc')
X_kr_cod, kr_cod_availability, kr_cod_names = featureStringVectorizer(kr_cod_str_list, 'kr_cod')

X_vi_ons_north, vi_ons_north_availability, vi_ons_north_names = featureStringVectorizer(vi_ons_north_str_list, 'vi_ons_north')
X_vi_nuc_north, vi_nuc_north_availability, vi_nuc_north_names = featureStringVectorizer(vi_nuc_north_str_list, 'vi_nuc_north')
X_vi_cod_north, vi_cod_north_availability, vi_cod_north_names = featureStringVectorizer(vi_cod_north_str_list, 'vi_cod_north')
X_vi_ton_north, vi_ton_north_availability, vi_ton_north_names = featureStringVectorizer(vi_ton_north_str_list, 'vi_ton_north')
X_vi_ons_central, vi_ons_central_availability, vi_ons_central_names = featureStringVectorizer(vi_ons_central_str_list, 'vi_ons_central')
X_vi_nuc_central, vi_nuc_central_availability, vi_nuc_central_names = featureStringVectorizer(vi_nuc_central_str_list, 'vi_nuc_central')
X_vi_cod_central, vi_cod_central_availability, vi_cod_central_names = featureStringVectorizer(vi_cod_central_str_list, 'vi_cod_central')
X_vi_ton_central, vi_ton_central_availability, vi_ton_central_names = featureStringVectorizer(vi_ton_central_str_list, 'vi_ton_central')
X_vi_ons_south, vi_ons_south_availability, vi_ons_south_names = featureStringVectorizer(vi_ons_south_str_list, 'vi_ons_south')
X_vi_nuc_south, vi_nuc_south_availability, vi_nuc_south_names = featureStringVectorizer(vi_nuc_south_str_list, 'vi_nuc_south')
X_vi_cod_south, vi_cod_south_availability, vi_cod_south_names = featureStringVectorizer(vi_cod_south_str_list, 'vi_cod_south')
X_vi_ton_south, vi_ton_south_availability, vi_ton_south_names = featureStringVectorizer(vi_ton_south_str_list, 'vi_ton_south')

X_yyef_jyutping_ons, yyef_jyutping_ons_availability, yyef_jyutping_ons_names = featureStringVectorizer(yyef_jyutping_ons_str_list, 'yyef_jyutping_ons')
X_yyef_jyutping_nuc, yyef_jyutping_nuc_availability, yyef_jyutping_nuc_names = featureStringVectorizer(yyef_jyutping_nuc_str_list, 'yyef_jyutping_nuc')
X_yyef_jyutping_cod, yyef_jyutping_cod_availability, yyef_jyutping_cod_names = featureStringVectorizer(yyef_jyutping_cod_str_list, 'yyef_jyutping_cod')
X_yyef_jyutping_ton, yyef_jyutping_ton_availability, yyef_jyutping_ton_names = featureStringVectorizer(yyef_jyutping_ton_str_list, 'yyef_jyutping_ton')

X_sh_IPA_onset, sh_IPA_onset_availability, sh_IPA_onset_names = featureStringVectorizer(sh_IPA_onset_str_list, 'sh_IPA_onset')
X_sh_IPA_rhyme, sh_IPA_rhyme_availability, sh_IPA_rhyme_names = featureStringVectorizer(sh_IPA_rhyme_str_list, 'sh_IPA_rhyme')
X_sh_IPA_tone, sh_IPA_tone_availability, sh_IPA_tone_names = featureStringVectorizer(sh_IPA_tone_str_list, 'sh_IPA_tone')

X_pinyin_onset, pinyin_onset_availability, pinyin_onset_names = featureStringVectorizer(pinyin_onset_str_list, 'pinyin_onset')
X_pinyin_rhyme, pinyin_rhyme_availability, pinyin_rhyme_names = featureStringVectorizer(pinyin_rhyme_str_list, 'pinyin_rhyme')
X_pinyin_tone, pinyin_tone_availability, pinyin_tone_names = featureStringVectorizer(pinyin_tone_str_list, 'pinyin_tone')

X = np.hstack((X_ja_on_ons, X_ja_on_nuc, X_ja_on_cod,
               X_kr_ons, X_kr_nuc, X_kr_cod,
               X_vi_ons_north, X_vi_nuc_north, X_vi_cod_north, X_vi_ton_north,
               X_vi_ons_central, X_vi_nuc_central, X_vi_cod_central, X_vi_ton_central,
               X_vi_ons_south, X_vi_nuc_south, X_vi_cod_south, X_vi_ton_south,
               X_yyef_jyutping_ons, X_yyef_jyutping_nuc, X_yyef_jyutping_cod, X_yyef_jyutping_ton,
               X_sh_IPA_onset, X_sh_IPA_rhyme, X_sh_IPA_tone,
               X_pinyin_onset, X_pinyin_rhyme, X_pinyin_tone))

X_names = ja_on_ons_names + ja_on_nuc_names + ja_on_cod_names + \
          kr_ons_names + kr_nuc_names + kr_cod_names + \
          vi_ons_north_names + vi_nuc_north_names + vi_cod_north_names + vi_ton_north_names + \
          vi_ons_central_names + vi_nuc_central_names + vi_cod_central_names + vi_ton_central_names + \
          vi_ons_south_names + vi_nuc_south_names + vi_cod_south_names + vi_ton_south_names + \
          yyef_jyutping_ons_names + yyef_jyutping_nuc_names + yyef_jyutping_cod_names + yyef_jyutping_ton_names + \
          sh_IPA_onset_names + sh_IPA_rhyme_names + sh_IPA_tone_names + \
          pinyin_onset_names + pinyin_rhyme_names + pinyin_tone_names

DIR_RESULTS = os.path.join(DIR_WORKING, 'results')
if not os.path.exists(DIR_RESULTS):
    os.makedirs(DIR_RESULTS)

with open(os.path.join(DIR_RESULTS, 'ChnCharData.csv'), 'w') as f:
    csv_writer = csv.writer(f, delimiter=',')
    csv_writer.writerow([n.encode('utf-8') for n in X_names])
    for r in X:
        csv_writer.writerow(r)

with open(os.path.join(DIR_RESULTS, 'ChnChar.csv'), 'w') as f:
    csv_writer = csv.writer(f, delimiter=',')
    csv_writer.writerow(["Unicode", "character"])
    for c in t_char_list:
        unicode_char = unichr(int(c.replace("U+", ""),16))
        csv_writer.writerow([c, unicode_char.encode('utf-8')])
