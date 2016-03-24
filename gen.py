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
    # print('cfd', cfd)
    if type(word) == tuple:
        # print(word(1), cfd[wcs][0])
        return (word[1], cfd[wcs][0])
    return cfd[wcs][0]

# def choose_tri(cfdist, )

def generate_model_random(cfdist, word, num=15):
    for i in range(num):
        print(word, end=' ')
        word = choose(cfdist, word)

def generate_model_random_sent(cfdist, word, num=15):
    t = [word[0]]
    dots = 0
    while dots <= num:
        t.append(word[1])
        word = choose(cfdist, word)
        dots = t.count('.')
    nicePrint(t)

def generate_from_text(text, num=15):
    f=open(text,'rU', encoding='utf-8')
    raw=f.read()
    f.close()
    tokens = nltk.word_tokenize(raw)
    text1 = nltk.Text(tokens)

    bigrams = nltk.bigrams(text1)

    # ile słów pojawia się tylko raz? 
    print(len(nltk.probability.FreqDist(text1).hapaxes())/len(set(text1)))

    trigrams = nltk.trigrams(text1)


    # print(list(trigrams)[:6])
    cfd = nltk.ConditionalFreqDist(bigrams)
    # cfd2 = nltk.ConditionalFreqDist(trigrams)
    cfd2 = nltk.ConditionalFreqDist(
               ( (x,y), z )
               for x, y, z in trigrams)


    word = gen_first_word(cfd)

    print(sorted(list(cfd2[word].items()), key = lambda x: x[1], reverse=True))
    print(word)
    # generate_model_random(cfd, word, num)
    print(word[0], end=" ")
    print()
    print('----- odpalam funkcję')
    generate_model_random_sent(cfd2, word, num)
    # intp = ["...", '?', '!', '.']
    # for k in cfd:
        # if k in intp:
            # print(sorted(list(cfd[k].items()), key = lambda x: x[1], reverse=True))

    # firstCandid = [a for k in cfd for a in cfd[k].items() if k in intp]
    # print(len(firstCandid))
    # print(len(oczysc(firstCandid)))
    # for c in cfd2:
        # if c[1] == '.':
            # print(sorted(list(cfd2[c].items()), key = lambda x: x[1], reverse=True))

######testy



def process(sentence):
    for (w1,t1), (w2,t2), (w3,t3) in nltk.trigrams(sentence):
        if (t1.startswith('V') and t2 == 'TO' and t3.startswith('V')):
            print(w1, w2, w3)

d = [(1,2), (1,3), ('a', 2), ('b',3), ('a',4)]
def oczysc(l):
    #fukncja sprawia ze dostajemy unique zliczenia słów z początku (porządek po zsumowaniu interp)
    d = {}
    for (w,n) in l:
        if w in d:
            d[w]+=n
        else:
            d[w]=n
    return list(d.items())

def gen_first_word(cfdst, intp= ("...", '?', '!', '.')):
    firstCandid = [a for k in cfdst for a in cfdst[k].items() if k in intp]
    cfd = sorted(oczysc(firstCandid), key = lambda x: x[1], reverse=True)
    wght = [n for (w, n) in cfd]
    wcs = weighted_choice_sub(wght)
    res = cfd[wcs][0]
    return res, choose(cfdst,res)


def game():
    con = True
    while(con):
        try:
            t = input("Give me path to the text please..\n")
            # w = input("Choose the word to start with..\n")
            n = int(input("How many sentences would you like the text to have?\n"))
            # generate_from_text(t,w,n)
            generate_from_text(t,n)
        except Exception as e:
            print(e)
        askcon = input('Would you like to continue? (y / n)\n')
        if askcon == 'n':
            con = False

# 
# game()
generate_from_text("teksty/witkacy-narkotyki.txt",7)

# generate_from_text()
