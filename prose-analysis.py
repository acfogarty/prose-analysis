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

  # parameters controlling analysis
  longSentenceCut = 35  # sentences are identified as 'too long' if nwords > longSentenceCut
  wordFreqCutFraction = 0.003  # all words, 2-grams and 3-grams which appear more than wordFreqCutFraction*nTotalWords times in the text will be printed
  ngramMax = 6  # find most common n-grams, from 2-grams to ngramMax-grams
  adverbFlag = True  # if True, find and highlight adverbs
  corpusCategory = 'fiction'  # corpus category to use when comparing word frequency in this text to word frequency in a corpus; possibilities are: 'adventure', 'belles_lettres', 'editorial', 'fiction', 'government', 'hobbies', 'humor', 'learned', 'lore', 'mystery', 'news', 'religion', 'reviews', 'romance', 'science_fiction'
  levenshteinCutoff = 0.5
  contextWindow = 7  # when checking if words close to each other in the text have similar sound/spelling, look at pairs of words within this window

  # start html file
  of = open('prose-analysis-output.html','w')
  writeHtmlHeader(of)

  # get prose file contents
  filename = sys.argv[1]
  of.write('<h1>Analysis of the file '+filename+'</h1>\n')
  ff = io.open(filename,'r',encoding="latin-1")
  raw = ff.read()
  ff.close()

  # process file contents
  processed = ''.join(i for i in raw if ord(i)<128)  # clean non-ascii characters
  regex = re.compile('<.*?>')
  processed = re.sub(regex, '', processed)  # clean html tags
  processedLower = processed.lower()
  wordTokens = nltk.word_tokenize(processedLower)  # break text into words
  sentenceTokens = nltk.sent_tokenize(processed)  # break text into sentences

  wordTokensNoStopwords = [w for w in wordTokens if w not in stopwords]
  wordTokensNoPunctuation = [w for w in wordTokens if w not in punctuation]

  # find overlong sentences, get mean and stdev of sentence length
  sentenceLengthHtml = analyseSentenceLength(sentenceTokens, longSentenceCut)
  of.write(sentenceLengthHtml)

  # find most frequent words (not including stopwords)
  mostFrequentWordsHtml = findFrequentWords(wordTokensNoStopwords, wordFreqCutFraction)
  of.write(mostFrequentWordsHtml)

  # compare word frequency to corpus word frequency
  freqVersusCorpusHtml = compareFrequentWordsToCorpus(wordTokens, corpusCategory)
  of.write(freqVersusCorpusHtml)

  # find most frequent n-grams
  mostFrequentNgramsHtml = findFrequentNgrams(wordTokensNoPunctuation, ngramMax, wordFreqCutFraction)
  of.write(mostFrequentNgramsHtml)

  # find adverbs
  adverbHtml = findAdverbs(sentenceTokens, adverbFlag)
  of.write(adverbHtml)

  # find repeated sentence starts
  sentStartHtml = findRepeatedSentenceStarts(sentenceTokens, ngramMax)
  of.write(sentStartHtml)

  # find similar words which are close together
  levenshteinHtml = findCloseWords(wordTokensNoPunctuation, contextWindow, distanceType='levenshtein', levenshteinCutoff=levenshteinCutoff)
  of.write(levenshteinHtml)

  # find similar-sounding words which are close together
  soundexHtml = findCloseWords(wordTokensNoPunctuation, contextWindow, distanceType='soundex')
  of.write(soundexHtml)

  # finish html file
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
  # of.write('  <link rel="stylesheet" href="stylesheet.css">\n')
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
 
  # color wordcount lightorange, orange or red depending on how far over longSentenceCut the sentence length is
  colorMap = {(longSentenceCut,int(longSentenceCut*1.2)): '#FFBF00', (int(longSentenceCut*1.2),int(longSentenceCut*1.4)): '#FF8000', (int(longSentenceCut*1.4),100000): '#FF0000'}  # TODO find nicer solution
  
  sentenceLengthHtml = '<h2>Long sentences (> '+str(longSentenceCut)+' words)</h2>\n'
  nLongSentences = 0
  sentenceLengths = []
  # break sentences into words
  for sentence in sentenceTokens:
    wordTokens = nltk.word_tokenize(sentence)
    nWords = len(wordTokens)
    sentenceLengths.append(nWords)
    if nWords > longSentenceCut:
      # get printing color
      for rangeTuple in colorMap.keys():
        if nWords > rangeTuple[0] and nWords <= rangeTuple[1]:
          color = colorMap[rangeTuple]
      # print to html
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

  # build frequency dictionary
  text = nltk.Text(wordTokensNoStopwords)
  fdist = nltk.FreqDist(text)

  # get words which appear >= wordFreqCut times and print to html
  nMostCommon = 1000
  reachedCut = False  # for checking if nMostCommon was big enough TODO is there a more elegant way to do this?
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
  freqCut = {2: wordFreqCut, 3: wordFreqCut}  # cut printing at different frequencies for different values of n 
  for n in xrange(4,ngramMax+1):
    freqCut[n] = 2
  print 'Printing all 2-grams and 3-grams that occur at least ',wordFreqCut,' times'
  print 'Printing all >3-grams that occur at least twice'

  # for each value of n, get n-grams which appear >= freqCut[n] times and print to html
  for n in xrange(2,ngramMax+1):
    mostFrequentNgramsHtml += '<h3>' + str(n) + '-grams</h3>\n'
    fdist = nltk.FreqDist(nltk.ngrams(wordTokensNoPunctuation, n))
    nMostCommon = 1000
    reachedCut = False  # for checking if nMostCommon was big enough TODO is there a more elegant way to do this?
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

  if adverbFlag:  # global variable

    sentenceHtml = ''

    nAdverbs = 0.0
    nWords = 0.0  # this will count each punctuation mark as a word, so isn't completely accurate

    for sentence in sentenceTokens:

      foundAdverb = False  # only print sentences in which at least one adverb was found

      try:
        taggedTokens = nltk.pos_tag(nltk.word_tokenize(sentence))
      except LookupError:
        adverbHtml += '<p>Cannot find adverbs because taggers/maxent_treebank_pos_tagger is not installed. Please use the NLTK Downloader to obtain the resource:  >>> nltk.download()</p>\n'
        return adverbHtml

      nWords += float(len(taggedTokens))

      # rebuild the sentence containing the highlighted adverb
      html = '<p>'
      for tagtuple in taggedTokens:
        if tagtuple[1] == 'RB':  # adverb
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
      
  else:  # if not adverbFlag

    adverbHtml += '<p>Adverbs not found because adverbFlag is set to False</p>'

  return adverbHtml


def compareFrequentWordsToCorpus(wordTokens, corpusCategory):
  '''compare word frequency in the text to word frequency in a corpus'''

  freqVersusCorpusHtml = '<h2>Word frequency compared to a corpus</h2>'
  freqVersusCorpusHtml += '<p>Category of corpus used: '+corpusCategory
  freqVersusCorpusHtml += '<p>Number shown = frequency with which the word appears in the input text, relative to the frequency with which it appears in the reference corpus (large set of example texts)</p>'
  freqVersusCorpusHtml += '<p>If the number is greater than 1, the word appears much more often in the text than in the corpus</p>'
  freqVersusCorpusHtml += '<p>If the number is less than 1, the word appears much less often in the text than in the corpus</p>'

  # build frequency dictionary for corpus text
  corpusText = brown.words(categories=corpusCategory)
  fdistCorpus = nltk.FreqDist(w.lower() for w in corpusText)
  totalCorpus = float(fdistCorpus.N())  # total number of words

  # build frequency dictionary for text (note: this is partially redundant with the dictionary in findFrequentWords)
  text = nltk.Text(wordTokens)
  fdistText = nltk.FreqDist(text)
  totalText = float(fdistText.N())  # total number of words

  htmlInCorpus = ''
  htmlNotInCorpus = ''
  relFreqDict = {}
  for word in fdistText.keys():
    if word not in fdistCorpus.keys():
      htmlNotInCorpus += '<p>' + word + ': not in corpus</p>'
    else:
      freqratio = fdistText[word]/totalText/fdistCorpus[word]*totalCorpus  # (frequency in text)/(frequency in corpus)
      relFreqDict[word] = freqratio

  # sort words by relative frequency
  for word in sorted(relFreqDict, key=relFreqDict.get):
    htmlInCorpus += '<p>' + word + ': '+str(relFreqDict[word])+'</p>'

  freqVersusCorpusHtml += htmlInCorpus
  freqVersusCorpusHtml += htmlNotInCorpus

  return freqVersusCorpusHtml


def findRepeatedSentenceStarts(sentenceTokens, ngramMax):
  '''find n-grams which are used more than once to start sentences, all n-grams up to ngramMax'''

  sentStartHtml = '<h2>Words and phrases frequently used to start sentences</h2>'

  ngrams = []
  for i in range(ngramMax):
    ngrams.append([])
 
  # collect words from start of every sentence
  for sentence in sentenceTokens:

    wordTokens = nltk.word_tokenize(sentence)
    wordTokensNoPunctuation = [w for w in wordTokens if w not in punctuation]
    maxPossWords = min(ngramMax, len(wordTokensNoPunctuation))

    for i in range(maxPossWords):
      ngrams[i].append(' '.join(wordTokensNoPunctuation[:i+1]))

  # count frequencies of n-grams
  for i in range(1,ngramMax+1):

    sentStartHtml += '<h3>' + str(i) + '-grams</h3>\n'
    countsToNgrams = {}

    for ngram in set(ngrams[i-1]):
      count = ngrams[i-1].count(ngram)
      if count > 1:
        if count in countsToNgrams.keys():
          countsToNgrams[count].append(ngram)
        else:
          countsToNgrams[count] = [ngram]

    # print from most to least frequent
    for count in reversed(sorted(countsToNgrams.keys())):
      for ngram in countsToNgrams[count]:
        sentStartHtml += '<p>' + ngram + ': ' + str(count) + '</p>\n'

  return sentStartHtml


def soundex(word):
    '''
    Convert word to soundex representation
    Input: string
    Output: string
    (Not the SQL implementation)'''

    soundex_map = {'b': '1',
                   'f': '1',
                   'p': '1',
                   'v': '1',
                   'c': '2',
                   'g': '2',
                   'j': '2',
                   'k': '2',
                   'q': '2',
                   's': '2',
                   'x': '2',
                   'z': '2',
                   'd': '3',
                   't': '3',
                   'l': '4',
                   'm': '5',
                   'n': '5',
                   'r': '6'}

    # Remove all occurrences of 'h' and 'w' except first letter
    first_letter = word[0]
    tail = word[1:].replace('h', '').replace('w', '')
    word = first_letter + tail

    # Replace all consonants (include the first letter) with digits
    # Replace all adjacent same digits with one digit
    soundex_string = ''
    for c in word:
        try:
            new_char = soundex_map[c]
            if new_char == soundex_string[:-1]:  # same digit twice in a row
                new_char = ''
        except KeyError:  # vowels
            new_char = c.upper()
        soundex_string += new_char

    # Remove all occurrences of a, e, i, o, u, y except first letter
    first_symbol = soundex_string[0]
    tail = ''.join(re.split(r'[AEIOUY]', soundex_string[1:]))
    # If first symbol is a digit replace it with letter saved earlier
    if first_symbol.isdigit():
        first_symbol = first_letter.upper()
    soundex_string = first_symbol + tail

    # 4 characters exactly
    while len(soundex_string) < 4:
        soundex_string += '0'                                 
    soundex_string = soundex_string[:4]                       
                                                              
    return soundex_string                              


def levenshteinDistance(string1, string2):

  len_string1 = len(string1)
  len_string2 = len(string2)

  if len_string2 > len_string1:
    return levenshteinDistance(string2, string1)

  array = np.zeros((len_string1 + 1, len_string2 + 1))
  array[:, 0] = range(len_string1 + 1)
  array[0, :] = range(len_string2 + 1)

  for i1 in range(1, len_string1 + 1):
    for i2 in range(1, len_string2 + 1):
      if string1[i1-1] == string2[i2-1]:
        substitute = array[i1-1, i2-1]
      else:
        substitute = array[i1-1, i2-1] + 1
      delete = array[i1 - 1, i2] + 1
      insert = array[i1, i2 - 1] + 1
      array[i1, i2] = min(delete, insert, substitute)

  return array[len_string1, len_string2]


def findCloseWords(wordTokens, contextWindow, distanceType='levenshtein', levenshteinCutoff=1):
  '''for a given deinition of similarity, find words which are similar and which are
  close together on the page
  'Close together' is defined as 'within a sliding window of size contextWindow'
  Criteria for deciding two words are similar are:
  - distanceType == levenshtein: levenshtein distance between two tokens is less than levenshteinCutoff
  - distanceType == soundex: two tokens have same soundex encoding

  input parameters:
  wordTokens: list of strings, should include stopwords so that sentences showing word context
              can be properly reconstructed
  contextWindow: integer, try to match word[i] to words in range word[i+1] to word[i+contextWindow]
  distanceType: string, 'levenshtein' or 'soundex'
  levenshteinCutoff: float, only needed if distanceType == 'levenshtein'
  '''

  if distanceType == 'levenshtein':
    closeHtml = '<h2>Similar words which are close together on the page</h2>'
  elif distanceType == 'soundex':
    closeHtml = '<h2>Similar-sounding words which are close together on the page</h2>'
  else:
    print('distanceType', distanceType, 'not recognised in function findCloseWords')
    quit()

  for i, word1 in enumerate(wordTokens):
    if i > len(wordTokens) - contextWindow:
      break
    for j in xrange(i+1, i+contextWindow):
      word2 = wordTokens[j]

      # use difference closeness checks for different distance types
      if distanceType == 'levenshtein':
        isClose = (levenshteinDistance(word1, word2)/np.mean((len(word1),len(word2))) < levenshteinCutoff)
      elif distanceType == 'soundex':
        isClose = (soundex(word1) == soundex(word2))

      if isClose:
        if (word1 not in stopwords) and (word2 not in stopwords):
          # rebuild the sentence containing the highlighted word
          closeHtml += '<p>'
          for k in xrange(i-contextWindow, j+contextWindow):
            if (k==i) or (k==j):
              closeHtml += '<span style="color: red">' + wordTokens[k] + '</span> ' 
            else:
              try:  # deal with fact we may be at end of file
                closeHtml += wordTokens[k] + ' '
              except IndexError:
                break
          closeHtml += '</p>\n'
          
  return closeHtml


if __name__ == '__main__':
  main() 
