import pandas as pd
import numpy as np
import itertools
import string
import re
from sklearn import preprocessing


def main():

  # get list of phones used, and labelled data (spelling to phonetic spelling)  
  phonesList, speltWords, phoneticWords = loadData()

  encode(speltWords, phoneticWords)

def loadData():
  '''load CMU dictionary
  returns:
     phonesList (symbols used in phonetic spelling)
     spellingToPhone (dict with keys=string containing original spelling, value=list of phones in string format)'''

  cmudictPath = '/Users/fogarty/code/nltk-analysis/cmudict'
  
  cmudictFile = cmudictPath + '/cmudict-0.7b-clean'
  cmudictPhonesFile = cmudictPath + '/cmudict-0.7b.phones'
  
  phonesList = pd.read_table(cmudictPhonesFile, sep='\s+', header=None)[0].tolist()

  speltWords = []
  phoneticWords = []
  enc = 'utf-8'
  ff = open(cmudictFile, 'r', encoding=enc, errors='replace')
  for line in ff:
    if line.startswith(';'):  # comment
      continue
    line = line.split()
    # get rid of numbers signalling emphasis
    for i,phone in enumerate(line[1:]):
      line[i+1] = re.sub(r'[0-9]',"",line[i+1])
     
    speltWords.append(line[0]) 
    phoneticWords.append(line[1:])
    # TODO filter out words with (1)

  return phonesList, speltWords, phoneticWords


def encode(speltWords, phoneticWords):

  max_length = len(max(speltWords, key=len))

  # list of strings to list of lists
  speltWords = list(map(list, speltWords))

  # convert to array of dimensions nsamples*max_length, padding with spaces
  X = np.array(list(itertools.zip_longest(*speltWords, fillvalue=' '))).T

  classes = list(string.printable)
  le = preprocessing.LabelEncoder()
  le.fit(classes)

  encoded_X = np.apply_along_axis(le.transform, 1, X)


if __name__ == '__main__':
  main() 
