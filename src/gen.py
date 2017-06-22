#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sys
import re
from functools import reduce

import nltk
from termcolor import cprint


# stuff just for printing
def get_color(dic, i):
    for n in sorted(dic.keys()):
        if n >= i:
            return dic[n]
    return dic[50]


def nicePrint(tab, freq):
    intp = ['.', ',', ';', '?', '!', ':', "'", '...']
    tab2 = [tab[0]]
    freq = [2] + freq
    colors = {1: 'grey', 10: 'green', 25: 'blue', 50: 'magenta'}
    for s in tab[1:]:
        if s not in intp:
            tab2.append(' ' + s)
        else:
            tab2.append(s)
    for i in range(len(tab2)):
        color = get_color(colors, freq[i])
        cprint(tab2[i], color, end='')
    print()


def parse_color_for_html(tab, freq):
    intp = ['.', ',', ';', '?', '!', ':', "'", '...']
    tab2 = [tab[0]]
    freq = [2] + freq
    colors = {1: 'grey', 10: 'green', 25: 'blue', 50: 'magenta'}
    for s in tab[1:]:
        if s not in intp:
            tab2.append(' ' + s)
        else:
            tab2.append(s)

    result = []
    for i in range(len(tab2)):
        color = get_color(colors, freq[i])
        # cprint(tab2[i], color, end='')
        result.append('<span class="res-{}">{}</span>'.format(color, tab2[i]))
    return ''.join(result)

# thanks to
# http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python#id1


def weighted_choice_sub(weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i


def choose(cfdist, word):
    cfd = sorted(list(cfdist[word].items()), key=lambda x: x[1], reverse=True)
    # tu by się przydało coś zrobić jak nie ma takiego słowa!
    # if len(cfd)>1:
    # print('AA!! Więcej niż jedna opcja - ', len(cfd),word)

    wght = [n for (w, n) in cfd]
    wcs = weighted_choice_sub(wght)
    # print('cfd', cfd)
    if type(word) == tuple:
        # print(word(1), cfd[wcs][0])
        return (word[1], cfd[wcs][0])

    return cfd[wcs][0]


def generate_model_random(cfdist, word, num=15):
    for i in range(num):
        print(word, end=' ')
        word = choose(cfdist, word)


def generate_model_random_sent(cfdist, word, num=15, prnt=True):
    t = [word[0]]
    dots = 0
    numOfChoices = []
    while dots < num:
        t.append(word[1])
        # tutaj komunikujemy ile mozliwcyh rozgalezien na tym słowie
        numOfChoices.append(len(list(cfdist[word].items())))
        word = choose(cfdist, word)
        dots = t.count('.')

    if prnt:

        # print(len(numOfChoices), len(t))
        nicePrint(t, numOfChoices)
        # print(t)
    html = parse_color_for_html(t, numOfChoices)
    # printowanie dziwnych rzeczy
    # print(numOfChoices)
    # print(sum([1 for n in numOfChoices if n > 1 ])/len(numOfChoices))
    # print(1 / reduce(lambda x, y: x*y, numOfChoices))
    # print(len([1 for n in numOfChoices if n == 1])/len(numOfChoices))

    counter, mounter = 0, 0
    for n in numOfChoices:
        if n == 1:
            mounter += 1
        else:
            counter = max(counter, mounter)
            mounter = 0
    # print("the longest streak: ", counter)
    old_text = re.sub('\s([^\w]{1,2}\s)', '\g<1>', ' '.join(t))

    import ipdb; ipdb.set_trace()  # breakpoint 60c1845e //s
    res = {'text': html,
           'data': (round(sum([1 for n in numOfChoices if n > 1]) / len(numOfChoices), 3),
                    reduce(lambda x, y: x * y, numOfChoices),
                    counter
                    )
           }

    return res


def generate_from_text(string=None, file=None, num=15, prnt=False):
    if not (string or file):
        return None
    elif file:
        f = open(file, 'rU', encoding='utf-8')
        raw = f.read()
        f.close()
    else:
        raw = string
    tokens = nltk.word_tokenize(raw)
    text1 = nltk.Text(tokens)

    bigrams = nltk.bigrams(text1)

    # ile słów pojawia się tylko raz?
    if prnt:
        print('Hapaxów: {:.1%}'.format(
            len(nltk.probability.FreqDist(text1).hapaxes()) / len(set(text1))))

    trigrams = nltk.trigrams(text1)

    # print(list(trigrams)[:6])
    cfd = nltk.ConditionalFreqDist(bigrams)
    # cfd2 = nltk.ConditionalFreqDist(trigrams)
    cfd2 = nltk.ConditionalFreqDist(
        ((x, y), z)
        for x, y, z in trigrams)

    word = gen_first_word(cfd)
    # print(word)
    # print(sorted(list(cfd2[word].items()), key = lambda x: x[1], reverse=True))

    # generate_model_random(cfd, word, num)
    if prnt:
        print('--Generated text:\n')
    model = generate_model_random_sent(cfd2, word, num, prnt)
    gm = model['data']
    averages = [[], [], []]
    result = model['text']

    for i in range(10):
        model = generate_model_random_sent(cfd2, word, num, False)
        gm = model['data']
        # print('Procent rozgalezien {:.1%} rząd wielkości drugiej miary: {} najdluzszy skopiowany fragment {}'.format(gm[0], len(str(gm[1])), gm[2]))
        averages[0].append(gm[0])
        averages[1].append(gm[1])
        averages[2].append(gm[2])

    avgs = [sum(a) / len(a) for a in averages]
    print('\n--Średnie: \n rozgalezien: {:.1%} ; rząd wielkości drugiej miary: {} najdluzszy skopiowany fragment {}'.format(
        avgs[0], len(str(avgs[1])), avgs[2]))

    return result
    # print(avgs)
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


# testy
d = [(1, 2), (1, 3), ('a', 2), ('b', 3), ('a', 4)]


def oczysc(l):
    # fukncja sprawia ze dostajemy unique zliczenia słów z początku (porządek
    # po zsumowaniu interp)
    d = {}
    for (w, n) in l:
        if w in d:
            d[w] += n
        else:
            d[w] = n
    return list(d.items())


def gen_first_word(cfdst, intp=("...", '?', '!', '.')):
    firstCandid = [a for k in cfdst for a in cfdst[k].items() if k in intp]
    cfd = sorted(oczysc(firstCandid), key=lambda x: x[1], reverse=True)
    wght = [n for (w, n) in cfd]
    wcs = weighted_choice_sub(wght)
    res = cfd[wcs][0]

    return res, choose(cfdst, res)


def game():
    while(True):
        try:
            t = input("Give me path to the text please..\n> ")
            # w = input("Choose the word to start with..\n")
            n = int(input("How many sentences would you like the text to have?\n> "))
            # generate_from_text(t,w,n)
            generate_from_text(file=t, num=n)
        except Exception as e:
            print(e)
        askcon = input('Would you like to continue? (y / n)\n> ')
        if askcon == 'n':
            break


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 3:
        try:
            generate_from_text(file="teksty/" + args[1], num=int(args[2]))
        except Exception as e:
            print("Something went wrong... ", e)
            game()
    else:
        game()
# for i in range(9, 17):
    # generate_from_text("teksty/wola-mocy.txt",i)

# generate_from_text()
