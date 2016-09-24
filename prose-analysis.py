import io
import sys
import re
sys.path.insert(1,'/Library/Python/2.7/site-packages')
import nltk
from nltk.corpus import stopwords

# global variables
stopwords = stopwords.words('english')
stopwords += ['.',',',';','?','!','-',':','',"n't","'d","'re","'s","'m"]
longSentenceCut = 45 #sentences are identified as 'too long' if nwords > longSentenceCut

def main():

  #start html file
  of = open('prose-analysis-output.html','w')
  writeHtmlHeader(of)

  #get file contents
  filename = sys.argv[1]
  of.write('<h1>Analysis of the file '+filename+'</h1>\n')
  ff = io.open(filename,'r',encoding="latin-1")
  raw = ff.read()
  ff.close()

  #process file contents
  processed = ''.join(i for i in raw if ord(i)<128) #clean non-ascii characters
  processedLower = raw.lower()
  longSentenceHtml = findLongSentences(processed, longSentenceCut)
  of.write(longSentenceHtml)
  #wordTokens = nltk.word_tokenize(processed)
  #wordTokensNoStopwords = [w for w in wordTokens if w not in stopwords]
  #text = nltk.Text(wordTokensNoStopwords)
  #fdist = nltk.FreqDist(text)

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
  of.write('</body>\n')
  of.write('</html>\n')

def findLongSentences(textString, longSentenceCut):
  '''identify sentences that contain more than longSentenceCut words and print them with a color code that depends on sentence length'''
  
  #color wordcount lightorange, orange or red depending on how far over longSentenceCut the sentence length is
  colorMap = {(longSentenceCut,int(longSentenceCut*1.2)): '#FFBF00', (int(longSentenceCut*1.2),int(longSentenceCut*1.4)): '#FF8000', (int(longSentenceCut*1.4),100000): '#FF0000'} #TODO find nicer solution
  
  #break text into sentences
  sentTokens = nltk.sent_tokenize(textString)
  print 'Found ',len(sentTokens),' sentences'

  longSentenceHtml = '<h2>Long sentences (> '+str(longSentenceCut)+' words)</h2>\n'
  nLongSentences = 0
  #break sentences into words
  for sentence in sentTokens:
    wordTokens = nltk.word_tokenize(sentence)
    nWords = len(wordTokens)
    if nWords > longSentenceCut:
      #get printing color
      for rangeTuple in colorMap.keys():
        if nWords > rangeTuple[0] and nWords <= rangeTuple[1]:
          color = colorMap[rangeTuple]
      #print to html
      html = '<p>' + sentence + ' - <span style="color:' + color + ';">' + str(nWords) + ' words</span></p>'
      longSentenceHtml += html
      nLongSentences += 1
  print 'Found ',nLongSentences,' long sentences'
  return longSentenceHtml

if __name__ == '__main__':
  main() 
