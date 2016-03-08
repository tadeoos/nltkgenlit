import nltk
import random

def nicePrint(tab):
    intp = ['.', ',', ';','?','!',':', "'", '...']
    tab2 = [tab[0]]
    for s in tab[1:]:
        if s not in intp:
            tab2.append(' ' + s)
        else:
            tab2.append(s)
    for s in tab2:
        print(s, end='')
        
#thanks to http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python#id1
def weighted_choice_sub(weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

def choose(cfdist, word):
	cfd = sorted(list(cfdist[word].items()), key = lambda x: x[1], reverse=True)
    # tu by się przydało coś zrobić jak nie ma takiego słowa!
	wght = [n for (w, n) in cfd]
	wcs = weighted_choice_sub(wght)
	return cfd[wcs][0]

def generate_model_random(cfdist, word, num=15):
    for i in range(num):
        print(word, end=' ')
        word = choose(cfdist, word)

def generate_model_random_sent(cfdist, word, num=15):
    t = []
    dots = 0
    while dots <= num:
        t.append(word)
        word = choose(cfdist, word)
        dots = t.count('.')
    nicePrint(t)

def generate_from_text(text, word, num=15):
    text1 = make_text(text)[0]
    bigrams = nltk.bigrams(text1)
    cfd = nltk.ConditionalFreqDist(bigrams)
    # generate_model_random(cfd, word, num)
    generate_model_random_sent(cfd, word, num)
    print('\n')


#we're about to add a function that tells us something about statistical similarity between a generated text and its parent.


#first we have to functionalize reading the text from a file, because we want to use sent_tokenize(method) and it seems taht it has to be done on raw text input.

def make_text(text):
    f=open(text,'rU', encoding='utf-8')
    raw=f.read()
    f.close()
    tokens = nltk.word_tokenize(raw)
    sents = nltk.sent_tokenize(raw)
    textOut = nltk.Text(tokens)
    # returning sth like this looks quite abominable; I hope it's only temporary
    return [textOut, len(sents), len(tokens)]

# for now it just returns the average sentence length and the number of times each vocabulary item appears in the text on average (so called 'lexical richness')
def simple_statistic(text):
    t = make_text(text)
    voc = len(set([word.lower() for word in t if word.isalpha()]))
    num_sent = t[1]
    num_words = t[2]
    return [round(num_words/num_sent), round(num_words/voc)]


    





def game():
    con = True
    while(con):
        t = input("Give me path to the text please..\n")
        w = input("Choose the word to start with..\n")
        n = int(input("How many sentences would you like the text to have?\n"))
        generate_from_text(t,w,n)
        askcon = input('Would you like to continue? (y / n)\n')
        if askcon == 'n':
            con = False


# game()
