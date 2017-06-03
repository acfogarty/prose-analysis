import pandas as pd
import numpy as np
import itertools
import string
import re
from sklearn import preprocessing


def main():

  # get list of phones used, and labelled data (spelling to phonetic spelling)  
  phonesList, speltWords, phoneticWords = loadData()

  # list of strings to list of lists
  speltWords = list(map(list, speltWords))

  # get all letters that could be in speltWords
  letters = list(string.printable)

  encoded_X = encode(speltWords, letters)

  encoded_Y = encode(phoneticWords, phonesList)

  print(encoded_Y[45:50])
  print(phoneticWords[45:50])


def loadData():
  '''load CMU dictionary
  returns:
     phonesList (symbols used in phonetic spelling)
     spellingToPhone (dict with keys=string containing original spelling, value=list of phones in string format)'''

  cmudictPath = '/Users/fogarty/code/nltk-analysis/cmudict'
  
  cmudictFile = cmudictPath + '/cmudict-0.7b-clean'
  cmudictPhonesFile = cmudictPath + '/cmudict-0.7b.phones'
  
  phonesList = pd.read_table(cmudictPhonesFile, sep='\s+', header=None)[0].tolist()
  phonesList += ' '

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


def encode(listListSymbols, symbolsSet):
  '''takes a list of lists of symbols (letters or phones), and the
  set of symbols in the list of lists
  Returns Label Encoding of the list of lists'''

  # max_length = len(max(speltWords, key=len))

  # convert to array of dimensions nsamples*max_length, padding with spaces
  X = np.array(list(itertools.zip_longest(*listListSymbols, fillvalue=' '))).T

  # encode letters/phones as integers
  le = preprocessing.LabelEncoder()
  le.fit(symbolsSet)
  print(le.classes_)

  encoded_X = np.apply_along_axis(le.transform, 1, X)

  return encoded_X


if __name__ == '__main__':
  main() 
