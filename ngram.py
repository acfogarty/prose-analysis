import sys
sys.path.insert(1,'/Library/Python/2.7/site-packages')
import nltk
from prose_analysis import loadProcessFile
from nltk.util import ngrams
from collections import defaultdict

# p(w1, w2, w3... wm) = PI_i=1^m p(w_i | w_i-n+1, ..., w_i-1) 
# p(w_i | w_i-n+1, ..., w_i-1) = count(w_i-n+1, ..., w_i-1, wi) / count(w_i-n+1, ..., w_i-1)

def main():

  n = 4

  filename = sys.argv[1]
  tokenized = loadProcessFile(filename)

  model = defaultdict(lambda: defaultdict(lambda: 0))

  # count(w_i-n+1, ..., w_i-1, wi)
  for sentence in tokenized['sentenceTokens']:
    for words_tuple in ngrams(nltk.word_tokenize(sentence.lower()), n, pad_right=True, pad_left=True):
      model[words_tuple[:-1]][words_tuple[-1]] += 1

  # p(w_i | w_i-n+1, ..., w_i-1) = count(w_i-n+1, ..., w_i-1, wi) / count(w_i-n+1, ..., w_i-1)
  for preceding_words_tuple in model:
    total_count = float(sum(model[preceding_words_tuple].values()))
    for wn in model[preceding_words_tuple]:
      model[preceding_words_tuple][wn] /= total_count
  
  print model[("all", "in", "the")]["first"] 
  print model[("in", "the", "hydration")]["layer"] 
  print model[("in", "the", "good")]["stuff"] 
  print model[None, None]["the"] 


if __name__ == '__main__':
    main()
