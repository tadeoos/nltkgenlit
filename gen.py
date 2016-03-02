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
    f=open(text,'rU', encoding='utf-8')
    raw=f.read()
    f.close()
    tokens = nltk.word_tokenize(raw)
    text1 = nltk.Text(tokens)
    bigrams = nltk.bigrams(text1)
    cfd = nltk.ConditionalFreqDist(bigrams)
    # generate_model_random(cfd, word, num)
    generate_model_random_sent(cfd, word, num)
    print('\n')


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


game()
