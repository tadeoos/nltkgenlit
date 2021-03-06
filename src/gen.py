#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sys
import re
import traceback
import os
from functools import reduce
from timeit import time

import nltk
from termcolor import cprint


def generate_cache(path, files):
    cache_dict = {}
    time_zero = time.time()
    for file in files:
        start_time = time.time()
        cprint('\n======= processing file {}...'.format(file), color='blue')
        f = open(os.path.join(path, file), 'rU', encoding='utf-8')
        raw = f.read()
        f.close()

        tokens = nltk.word_tokenize(raw)
        book = nltk.Text(tokens)
        hapaxes = len(nltk.probability.FreqDist(
            book).hapaxes()) / len(set(book))
        vocab_count = len(set(book))
        print(
            '=== {:.2f}s -- Text class initialized'.format(time.time() - start_time))

        bigrams = nltk.bigrams(book)
        bi_cfd = nltk.ConditionalFreqDist(bigrams)
        print('=== {:.2f}s -- bigrams done'.format(time.time() - start_time))

        trigrams = nltk.trigrams(book)
        tri_cfd = nltk.ConditionalFreqDist(((x, y), z) for x, y, z in trigrams)
        print('=== {:.2f}s -- trigrams done'.format(time.time() - start_time))

        file_dict = {'bigrams': bi_cfd, 'trigrams': tri_cfd}
        cache_dict['{}'.format(file)] = file_dict
        cache_dict['{}'.format(file)].update(
            {'hap': hapaxes, 'v_count': vocab_count})
        cprint('====== {:.2f}s -- cached {}'.format(time.time() -
                                                    start_time, file), color='green')

    cprint('\n\n=========== CACHE TOOKED {:.2f} seconds\n =========='.format(
        time.time() - time_zero), color='yellow')
    return cache_dict

# stuff just for printing


def get_color(dic, i):
    colors = sorted(dic.keys())
    for n in colors:
        if n >= i:
            return dic[n]
    return dic[colors[-1]]


def clean(text):
    interp = ("''", '"')
    in_quote = False
    list_of_words = text.split()
    clean_data = []
    for i, token in enumerate(list_of_words):
        if i > 0 and list_of_words[i - 1][-1] == ',':
            clean_data.append(token + ' ')
            continue
        elif not in_quote:
            if token in interp:
                in_quote = True
                clean_data.append(token)
            else:
                clean_data.append(token + ' ')
        elif in_quote:
            if token in interp:
                in_quote = False
                clean_data.append(token + ' ')
            elif i == len(list_of_words) - 1:
                clean_data.append(token)
            elif list_of_words[i + 1] in interp:
                clean_data.append(token)
            else:
                clean_data.append(token + ' ')
        else:
            clean_data.append(token + ' ')
    return ''.join(clean_data)


def nicePrint(tab, freq, start=1, html=False):
    intp = ['.', ',', ';', '?', '!', ':', '’', "'", '...']
    quotes = ['"', '`', "”", "``"]
    tab2 = [tab[0]]
    freq = [start] + freq
    colors = {1: 'grey', 10: 'green', 25: 'blue', 50: 'magenta', 100: 'yellow'}
    # prepare for printing, no spaces around interp
    for i, word in enumerate(tab[1:]):
        if word in intp:
            tab2.append(word)
        elif word in quotes:
            if word in tab[:i]:
                tab2.append(word)
            else:
                tab2.append(' ' + word)
        elif tab2[i].strip() in quotes and tab2[i][0] == " ":
            tab2.append(word)
        else:
            tab2.append(' ' + word)

    if html:
        result = []
        for i in range(len(tab2)):
            color = get_color(colors, freq[i])
            result.append(
                "<span class='res-{}'>{}</span>".format(color, tab2[i]))
        return ''.join(result)

    for i in range(len(tab2)):
        color = get_color(colors, freq[i])
        cprint(tab2[i], color, end='')
    print()


# thanks to
# http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python#id1


def weighted_choice_sub(weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i


def choose(cfdist, word, first=None):
    cfd = sorted(list(cfdist[word].items()), key=lambda x: x[1], reverse=True)
    # tu by się przydało coś zrobić jak nie ma takiego słowa!
    # if len(cfd)>1:
    # print('AA!! Więcej niż jedna opcja - ', len(cfd),word)

    wght = [n for (w, n) in cfd]
    wcs = weighted_choice_sub(wght)
    # print('cfd', cfd)

    if type(word) == tuple:
        # print(word(1), cfd[wcs][0])
        try:
            return (word[1], cfd[wcs][0])
        except TypeError:
            return ('.', first)
    return cfd[wcs][0]


def generate_model_random(cfdist, word, num=15):
    for i in range(num):
        print(word, end=' ')
        word = choose(cfdist, word)


def generate_model_random_sent(cfdist, word, num=15, prnt=True, first_choice=2):
    first_word = word[0]
    t = [word[0]]
    dots = 0
    numOfChoices = [len(list(cfdist[('.', word[0])].items()))]
    while dots < num:
        t.append(word[1])
        # tutaj komunikujemy ile mozliwcyh rozgalezien na tym słowie
        numOfChoices.append(len(list(cfdist[word].items())))
        word = choose(cfdist, word, first=first_word)
        dots = t.count('.')
    if prnt:
        nicePrint(t, numOfChoices, start=first_choice)

    html = nicePrint(t, numOfChoices, html=True, start=first_choice)

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

    old_text = re.sub('\s([^\w]{1,2}\s)', '\g<1>', ' '.join(t))

    res = {'raw': old_text,
           'html': html,
           'stats': (round(sum([1 for n in numOfChoices if n > 1]) / len(numOfChoices), 3),
                     reduce(lambda x, y: x * y, numOfChoices),
                     counter)
           }

    return res


def generate_from_text(string=None, file=None, num=15, prnt=False, cache=None):
    if not (string or file):
        return None
    elif file:
        f = open(file, 'rU', encoding='utf-8')
        raw = f.read()
        f.close()
    else:
        raw = string

    # if cache:
    #     bigrams = cache[book]['bigrams']
    #     trigrams = cache[book]'trigrams']
    # else:
    #     bigrams = nltk.bigrams(book)
    #     trigrams = nltk.trigrams(book)

    if cache:
        just_file = os.path.basename(os.path.normpath(file))
        hapaxes = cache[just_file]['hap']
        vocab_count = cache[just_file]['v_count']
        bigram_cfd = cache[just_file]['bigrams']
        trigram_cfd = cache[just_file]['trigrams']
    else:
        tokens = nltk.word_tokenize(raw)
        book = nltk.Text(tokens)
        try:
            hapaxes = len(nltk.probability.FreqDist(
                book).hapaxes()) / len(set(book))
        except ZeroDivisionError:
            print(book)
            hapaxes = 0
        vocab_count = len(set(book))
        bigrams = nltk.bigrams(book)
        trigrams = nltk.trigrams(book)
        bigram_cfd = nltk.ConditionalFreqDist(bigrams)
        trigram_cfd = nltk.ConditionalFreqDist(
            ((x, y), z) for x, y, z in trigrams)

    first_word = gen_first_word(bigram_cfd)

    if prnt:
        print('Hapaxów: {:.1%}'.format(hapaxes))
        print('--Generated text:\n')
    try:
        model = generate_model_random_sent(trigram_cfd, word=first_word[
            'word'], num=num, prnt=prnt, first_choice=first_word['choice'])
        gm = model['stats']
    except Exception as e:
        print('INDEX ERROR: ', e)
        print(traceback.print_exc())
        model = {'text': '<span class="res-text">There was an error :(</span>'}

    return model


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


def gen_first_word(cfdst, intp=('.')):
    firstCandid = [list(cfdst[word].items()) for word in cfdst if word in intp][
        0]  # get word, number tuple of all after interp
    cfd = sorted(oczysc(firstCandid), key=lambda x: x[1], reverse=True)
    wght = [n for (w, n) in cfd]
    wcs = weighted_choice_sub(wght)
    res = cfd[wcs][0]
    return {'word': (res.title(), choose(cfdst, res)), 'choice': len(wght)}


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
            generate_from_text(
                file="teksty/" + args[1], num=int(args[2]), prnt=1)
        except Exception as e:
            print("Something went wrong... ", e)
            game()
    else:
        game()
