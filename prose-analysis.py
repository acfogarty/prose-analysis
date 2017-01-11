import io
import sys
import re
sys.path.insert(1,'/Library/Python/2.7/site-packages')
import nltk
from nltk.corpus import stopwords
from nltk.corpus import brown
import numpy as np

# usage: python prose-analysis.py file-to-be-analysed

# global variables
stopwords = stopwords.words('english')
punctuation = ['.',',',';','?','!','-',':','',"n't","'d","'re","'s","'m",'``','"','--',"''",'(',')']
stopwords += punctuation

def main():

  #parameters controlling analysis
  longSentenceCut = 35 #sentences are identified as 'too long' if nwords > longSentenceCut
  wordFreqCutFraction = 0.003 #all words, 2-grams and 3-grams which appear more than wordFreqCutFraction*nTotalWords times in the text will be printed
  ngramMax = 6 #find most common n-grams, from 2-grams to ngramMax-grams
  adverbFlag = True #if True, find and highlight adverbs
  corpusCategory = 'fiction' #corpus category to use when comparing word frequency in this text to word frequency in a corpus; possibilities are: 'adventure', 'belles_lettres', 'editorial', 'fiction', 'government', 'hobbies', 'humor', 'learned', 'lore', 'mystery', 'news', 'religion', 'reviews', 'romance', 'science_fiction'

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
  processedLower = processed.lower()
  wordTokens = nltk.word_tokenize(processedLower) #break text into words
  sentenceTokens = nltk.sent_tokenize(processed) #break text into sentences

  wordTokensNoStopwords = [w for w in wordTokens if w not in stopwords]
  wordTokensNoPunctuation = [w for w in wordTokens if w not in punctuation]

  #find overlong sentences, get mean and stdev of sentence length
  sentenceLengthHtml = analyseSentenceLength(sentenceTokens, longSentenceCut)
  of.write(sentenceLengthHtml)

  #find most frequent words (not including stopwords)
  mostFrequentWordsHtml = findFrequentWords(wordTokensNoStopwords, wordFreqCutFraction)
  of.write(mostFrequentWordsHtml)

  #compare word frequency to corpus word frequency
  freqVersusCorpusHtml = compareFrequentWordsToCorpus(wordTokens, corpusCategory)
  of.write(freqVersusCorpusHtml)

  #find most frequent n-grams
  mostFrequentNgramsHtml = findFrequentNgrams(wordTokensNoPunctuation, ngramMax, wordFreqCutFraction)
  of.write(mostFrequentNgramsHtml)

  #find adverbs
  adverbHtml = findAdverbs(sentenceTokens,adverbFlag)
  of.write(adverbHtml)

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

def analyseSentenceLength(sentenceTokens, longSentenceCut):
  '''identify sentences that contain more than longSentenceCut words and print them with a color code that depends on sentence length; get mean and standard deviation of sentence length'''
 
  #color wordcount lightorange, orange or red depending on how far over longSentenceCut the sentence length is
  colorMap = {(longSentenceCut,int(longSentenceCut*1.2)): '#FFBF00', (int(longSentenceCut*1.2),int(longSentenceCut*1.4)): '#FF8000', (int(longSentenceCut*1.4),100000): '#FF0000'} #TODO find nicer solution
  
  sentenceLengthHtml = '<h2>Long sentences (> '+str(longSentenceCut)+' words)</h2>\n'
  nLongSentences = 0
  sentenceLengths = []
  #break sentences into words
  for sentence in sentenceTokens:
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
  print 'Found ',nTotalWords,' words, excluding stopwords'
  wordFreqCut = int(nTotalWords*wordFreqCutFraction)
  print 'Printing all words that occur at least ',wordFreqCut,' times'
  mostFrequentWordsHtml += '<p>Printing all words that occur at least ' + str(wordFreqCut) + ' times.'
  if stopwordsExcluded: 
    mostFrequentWordsHtml += " Stopwords (such as 'the', 'a', 'in', 'of' etc.) are not included.</p>\n"
  else:
    mostFrequentWordsHtml += '</p>\n'

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

def findAdverbs(sentenceTokens,adverbFlag):
  '''print adverb-containing sentences with the adverbs highlighted in red'''

  adverbHtml = '<h2>Adverbs</h2>\n'

  if adverbFlag: #global variable

    sentenceHtml = ''

    nAdverbs = 0.0
    nWords = 0.0 #this will count each punctuation mark as a word, so isn't completely accurate

    for sentence in sentenceTokens:

      foundAdverb = False #only print sentences in which at least one adverb was found

      try:
        taggedTokens = nltk.pos_tag(nltk.word_tokenize(sentence))
      except LookupError:
        adverbHtml += '<p>Cannot find adverbs because taggers/maxent_treebank_pos_tagger is not installed. Please use the NLTK Downloader to obtain the resource:  >>> nltk.download()</p>\n'
        return adverbHtml

      nWords += float(len(taggedTokens))

      #rebuild the sentence containing the highlighted adverb
      html = '<p>'
      for tagtuple in taggedTokens:
        if tagtuple[1] == 'RB': #adverb
          html += '<span style="color: red">' + tagtuple[0] + '</span> ' 
          foundAdverb = True
          nAdverbs += 1.0
        else:
          html += tagtuple[0] + ' '
      if foundAdverb:
        html += '</p>\n'
        sentenceHtml += html

    adverbHtml += '<p>Your text is %4.2f%% adverbs.</p>\n' % (nAdverbs/nWords*100.0) 
    adverbHtml += sentenceHtml    
      
  else: #if not adverbFlag

    adverbHtml += '<p>Adverbs not found because adverbFlag is set to False</p>'

  return adverbHtml

def compareFrequentWordsToCorpus(wordTokens, corpusCategory):
  '''compare word frequency in the text to word frequency in a corpus'''

  freqVersusCorpusHtml = '<h2>Word frequency compared to a corpus</h2>'
  freqVersusCorpusHtml += '<p>Category of corpus used: '+corpusCategory
  freqVersusCorpusHtml += '<p>Number shown = frequency with which the word appears in the input text, relative to the frequency with which it appears in the reference corpus (large set of example texts)</p>'
  freqVersusCorpusHtml += '<p>If the number is greater than 1, the word appears much more often in the text than in the corpus</p>'
  freqVersusCorpusHtml += '<p>If the number is less than 1, the word appears much less often in the text than in the corpus</p>'

  #build frequency dictionary for corpus text
  corpusText = brown.words(categories=corpusCategory)
  fdistCorpus = nltk.FreqDist(w.lower() for w in corpusText)
  totalCorpus = float(fdistCorpus.N()) #total number of words

  #build frequency dictionary for text (note: this is partially redundant with the dictionary in findFrequentWords)
  text = nltk.Text(wordTokens)
  fdistText = nltk.FreqDist(text)
  totalText = float(fdistText.N()) #total number of words

  htmlInCorpus = ''
  htmlNotInCorpus = ''
  relFreqDict = {}
  for word in fdistText.keys():
    if word not in fdistCorpus.keys():
      htmlNotInCorpus += '<p>' + word + ': not in corpus</p>'
    else:
      freqratio = fdistText[word]/totalText/fdistCorpus[word]*totalCorpus #(frequency in text)/(frequency in corpus)
      relFreqDict[word] = freqratio

  #sort words by relative frequency
  for word in sorted(relFreqDict, key=relFreqDict.get):
    htmlInCorpus += '<p>' + word + ': '+str(relFreqDict[word])+'</p>'

  freqVersusCorpusHtml += htmlInCorpus
  freqVersusCorpusHtml += htmlNotInCorpus

  return freqVersusCorpusHtml


if __name__ == '__main__':
  main() 
