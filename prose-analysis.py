import io
import sys
import re
sys.path.insert(1,'/Library/Python/2.7/site-packages')
import nltk
from nltk.corpus import stopwords
import numpy as np

# usage: python prose-analysis.py file-to-be-analysed

# global variables
stopwords = stopwords.words('english')
punctuation = ['.',',',';','?','!','-',':','',"n't","'d","'re","'s","'m",'``','"','--',"''"]
stopwords += punctuation

def main():

  #parameters controlling analysis
  longSentenceCut = 45 #sentences are identified as 'too long' if nwords > longSentenceCut
  wordFreqCutFraction = 0.004 #all words, 2-grams and 3-grams which appear more than wordFreqCutFraction*nTotalWords times in the text will be printed
  ngramMax = 7 #find most common n-grams, from 2-grams to ngramMax-grams

  #start html file
  of = open('prose-analysis-output.html','w')
  writeHtmlHeader(of)

  #get prose file contents
  filename = sys.argv[1]
  of.write('<h1>Analysis of the file '+filename+'</h1>\n')
  ff = io.open(filename,'r',encoding="latin-1")
  raw = ff.read()
  ff.close()

  #process file contents
  processed = ''.join(i for i in raw if ord(i)<128) #clean non-ascii characters
  processedLower = raw.lower()
  wordTokens = nltk.word_tokenize(processedLower)
  wordTokensNoStopwords = [w for w in wordTokens if w not in stopwords]
  wordTokensNoPunctuation = [w for w in wordTokens if w not in punctuation]

  #find overlong sentences, get mean and stdev of sentence length
  sentenceLengthHtml = analyseSentenceLength(processed, longSentenceCut)
  of.write(sentenceLengthHtml)

  #find most frequent words (not including stopwords)
  mostFrequentWordsHtml = findFrequentWords(wordTokensNoStopwords, wordFreqCutFraction)
  of.write(mostFrequentWordsHtml)

  #find most frequent n-grams
  mostFrequentNgramsHtml = findFrequentNgrams(wordTokensNoPunctuation, ngramMax, wordFreqCutFraction)
  of.write(mostFrequentNgramsHtml)

  #finish html file
  writeHtmlFooter(of)
  of.close()

def writeHtmlHeader(of):
  '''write the start of the html output file'''
  of.write('<!doctype html>\n')
  of.write('\n')
  of.write('<html lang="en">\n')
  of.write('<head>\n')
  of.write('  <meta charset="utf-8">\n')
  of.write('\n')
  of.write('  <title>Prose analysis tool</title>\n')
  of.write('  <meta name="description" content="prose analysis tool">\n')
  of.write('  <meta name="author" content="acfogarty">\n')
  of.write('\n')
  #of.write('  <link rel="stylesheet" href="stylesheet.css">\n')
  of.write('\n')
  of.write('</head>\n')
  of.write('\n')
  of.write('<body>\n')

def writeHtmlFooter(of):
  '''write the end of the html output file'''
  of.write('\n')
  of.write('</body>\n')
  of.write('</html>\n')

def analyseSentenceLength(textString, longSentenceCut):
  '''identify sentences that contain more than longSentenceCut words and print them with a color code that depends on sentence length; get mean and standard deviation of sentence length'''
  
  #color wordcount lightorange, orange or red depending on how far over longSentenceCut the sentence length is
  colorMap = {(longSentenceCut,int(longSentenceCut*1.2)): '#FFBF00', (int(longSentenceCut*1.2),int(longSentenceCut*1.4)): '#FF8000', (int(longSentenceCut*1.4),100000): '#FF0000'} #TODO find nicer solution
  
  #break text into sentences
  sentTokens = nltk.sent_tokenize(textString)
  print 'Found ',len(sentTokens),' sentences'

  sentenceLengthHtml = '<h2>Long sentences (> '+str(longSentenceCut)+' words)</h2>\n'
  nLongSentences = 0
  sentenceLengths = []
  #break sentences into words
  for sentence in sentTokens:
    wordTokens = nltk.word_tokenize(sentence)
    nWords = len(wordTokens)
    sentenceLengths.append(nWords)
    if nWords > longSentenceCut:
      #get printing color
      for rangeTuple in colorMap.keys():
        if nWords > rangeTuple[0] and nWords <= rangeTuple[1]:
          color = colorMap[rangeTuple]
      #print to html
      html = '<p>' + sentence + ' - <span style="color:' + color + ';">' + str(nWords) + ' words</span></p>\n'
      sentenceLengthHtml += html
      nLongSentences += 1

  print 'Found ',nLongSentences,' long sentences'

  sentenceLengths = np.asarray(sentenceLengths)
  sentenceLengthHtml += '<h2>Sentence length variability</h2>\n'
  sentenceLengthHtml += '<p>Longest sentence: ' + str(sentenceLengths.max()) + ' words</p>\n'
  sentenceLengthHtml += '<p>Shortest sentence: ' + str(sentenceLengths.min()) + ' words</p>\n'
  sentenceLengthHtml += '<p>Average sentence length: ' + '%4.2f' % sentenceLengths.mean() + ' words</p>\n'
  sentenceLengthHtml += '<p>Standard deviation of sentence length: ' + '%4.2f' % sentenceLengths.std() + ' words</p>\n'

  return sentenceLengthHtml

def findFrequentWords(wordTokensNoStopwords, wordFreqCutFraction, stopwordsExcluded=True):
  '''find all words which appear more than wordFreqCutFraction*nTotalWords times in the text, i.e. the number of occurences above which a word is defined as frequent is a function of the total number of words in the document'''

  mostFrequentWordsHtml = '<h2>Most frequently used words</h2>\n'
  nTotalWords = len(wordTokensNoStopwords)
  print 'Found ',nTotalWords,' words'
  wordFreqCut = int(nTotalWords*wordFreqCutFraction)
  print 'Printing all words that occur at least ',wordFreqCut,' times'
  mostFrequentWordsHtml += '<p>Printing all words that occur at least ' + str(wordFreqCut) + ' times</p>'
  if stopwordsExcluded: mostFrequentWordsHtml += "<p>Stopwords (such as 'the', 'a', 'in', 'of' etc.) are not included</p>\n"

  #build frequency dictionary
  text = nltk.Text(wordTokensNoStopwords)
  fdist = nltk.FreqDist(text)

  #get words which appear >= wordFreqCut times and print to html
  nMostCommon = 1000
  reachedCut = False #for checking if nMostCommon was big enough TODO is there a more elegant way to do this?
  for word,freq in fdist.most_common(nMostCommon): 
    if freq < wordFreqCut:
      reachedCut = True
      break
    html = '<p>' + word + ': ' + str(freq) + '</p>\n'
    mostFrequentWordsHtml += html
  if not reachedCut:
    print 'Error! the value of nMostCommon in findFrequentWords was not big enough'
    quit()

  return mostFrequentWordsHtml

def findFrequentNgrams(wordTokensNoPunctuation, ngramMax, wordFreqCutFraction):
  '''find all 2-grams and 3-grams which appear more than wordFreqCutFraction*nTotalWords times in the text, and all >3-grams which appear more than once'''

  mostFrequentNgramsHtml = '<h2>Most frequently used n-grams</h2>\n'
  nTotalWords = len(wordTokensNoPunctuation)
  wordFreqCut = int(nTotalWords*wordFreqCutFraction)
  freqCut = {2: wordFreqCut, 3: wordFreqCut} #cut printing at different frequencies for different values of n 
  for n in xrange(4,ngramMax+1):
    freqCut[n] = 2
  print 'Printing all 2-grams and 3-grams that occur at least ',wordFreqCut,' times'
  print 'Printing all >3-grams that occur at least twice'

  #for each value of n, get n-grams which appear >= freqCut[n] times and print to html
  for n in xrange(2,ngramMax+1):
    mostFrequentNgramsHtml += '<h3>' + str(n) + '-grams</h3>\n'
    fdist = nltk.FreqDist(nltk.ngrams(wordTokensNoPunctuation, n))
    nMostCommon = 1000
    reachedCut = False #for checking if nMostCommon was big enough TODO is there a more elegant way to do this?
    for ngram,freq in fdist.most_common(nMostCommon): 
      if freq < freqCut[n]:
        reachedCut = True
        break
      html = '<p>'
      for word in ngram:
        html += word + ' '
      html += ': ' + str(freq) + '</p>\n'
      mostFrequentNgramsHtml += html
    if not reachedCut:
      print 'Error! the value of nMostCommon in findFrequentNgrams was not big enough for n = ',n
      quit()

  return mostFrequentNgramsHtml

if __name__ == '__main__':
  main() 
