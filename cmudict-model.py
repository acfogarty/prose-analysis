import pandas as pd
import re


def main():

  # get list of phones used, and labelled data (spelling to phonetic spelling)  
  phonesList, spellingToPhone = loadData()

  print(spellingToPhone)


def loadData():
  '''load CMU dictionary
  returns:
     phonesList (symbols used in phonetic spelling)
     spellingToPhone (dict with keys=string containing original spelling, value=list of phones in string format)'''

  cmudictPath = '/Users/fogarty/code/nltk-analysis/cmudict'
  
  cmudictFile = cmudictPath + '/cmudict-0.7b-clean'
  cmudictPhonesFile = cmudictPath + '/cmudict-0.7b.phones'
  
  phonesList = pd.read_table(cmudictPhonesFile, sep='\s+', header=None)[0].tolist()

  spellingToPhone = {}
  enc = 'utf-8'
  ff = open(cmudictFile, 'r', encoding=enc, errors='replace')
  for line in ff:
    if line.startswith(';'):  # comment
      continue
    line = line.split()
    # get rid of numbers signalling emphasis
    for i,phone in enumerate(line[1:]):
      line[i+1] = re.sub(r'[0-9]',"",line[i+1])
      
    spellingToPhone[line[0]] = line[1:]

  return phonesList, spellingToPhone


if __name__ == '__main__':
  main() 
