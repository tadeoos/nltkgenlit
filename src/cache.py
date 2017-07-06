import sys
import os
from timeit import time
import nltk
import json
from nltk.util import trigrams, bigrams
from termcolor import cprint
from pympler import asizeof
from timeit import time
from humanize import naturalsize
from itertools import islice
from ast import literal_eval

def change_freqD(freq, maping):
    res={}
    for k,v in freq.items():
        res.update({maping[k]:v})
    return res

def pair_map(w1, w2):
    sec = str(w2)
    return int('{}{}'.format(w1, sec.zfill(7)))

def unpair_map(word):
    try:
        w = str(word)
        return int(w[:-7]), int(w[-7:])
    except:
        print(w)
        raise

def encode(maping, cfd):
    res = {}
    for el in cfd.items():
        try:
            if type(el[0])==str:
                new_k = maping[el[0]]
            else:
                w1, w2 = el[0]
                new_k = pair_map(maping[w1],maping[w2])
        except Exception as e:
            print(e)
            import ipdb; ipdb.set_trace()  # breakpoint 161a43f8 //
            raise
        freq_dist = change_freqD(el[1], maping)
        res.update({new_k: freq_dist})

    return res

def reverse_map(maping, val, size=2):
    # print(val)
    try:
        if size == 2:
            return [k for k, v in maping.items() if v==int(val)][0]
        else:
            return tuple([k for k, v in maping.items() if int(v) in val])
    except Exception as e:
        print(e)
        print(val)
        print([k for k, v in maping.items()])
        raise

def get_cfd_tail(maping, d):
    return {reverse_map(maping, k) for k,v in d.items()}


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


def decode_file(cache_raw):
    cache = json.loads(cache_raw)
    result = {}
    # maping = cache['map']
    
    try:
        n_cache = take(20, cache['trigrams_d'].items())
        # n_maping = take(20, maping.items())
        # print(n_cache)
        # for c in n_cache:
        #     print(c[0] in maping.values())
        # print(n_maping)
        # bigrams = { reverse_map(maping, k) : get_cfd_tail(maping, v) for k, v in cache['bigrams_d'].items()}
        # print('bigrams DONE')

        trigrams = { literal_eval(k):v for k, v in cache['trigrams_d'].items()}
    except Exception as e:
        # import ipdb; ipdb.set_trace()  # breakpoint 40b515cb //
        raise

    return { 'bigrams': cache['bigrams_d'], 'trigrams': trigrams, 
              'v_count': cache['v_count'], 'hap': cache['hap']}


def cache_file(q, path, file):
    f = open(os.path.join(path, file), 'r', encoding='utf-8')
    raw = f.read()
    f.close()

    tokens = nltk.word_tokenize(raw)
    book = nltk.Text(tokens)
    vocab = set(book)
    hapaxes = len(nltk.probability.FreqDist(book).hapaxes()) / len(vocab)
    vocab_count = len(vocab)
    word_mapping = {e:i for i,e in enumerate(vocab)}

    bi_cfd = nltk.ConditionalFreqDist(bigrams(book))
    tri_cfd = nltk.ConditionalFreqDist(((x, y), z) for x, y, z in trigrams(book))
    
    cprint('BIGRAM SIZE: {}'.format(naturalsize(asizeof.asizeof(bi_cfd, detail=1))), 'grey')
    cprint('TRIGRAM SIZE: {}'.format(naturalsize(asizeof.asizeof(tri_cfd, detail=1))), 'grey')
    cprint('MAP SIZE: {}'.format(naturalsize(asizeof.asizeof(word_mapping, detail=1))), 'grey')

    t1 = time.time()
    bi_compress = encode(word_mapping, bi_cfd)
    tri_compressed = encode(word_mapping, tri_cfd)
    file_dict = {'bigrams_d': bi_compress, 'trigrams_d': tri_compressed, 
                    'hap': hapaxes, 'v_count': vocab_count, 'map': word_mapping}
    old = {'bigrams_d': bi_cfd, 'trigrams_d': {str(k):v for k,v in tri_cfd.items()}, 
                    'hap': hapaxes, 'v_count': vocab_count}
    

    js = json.dumps(file_dict)
    js2 = json.dumps(old)
    t2= time.time()

    # print('COMP SIZE: {} bytes'.format(asizeof.asizeof(tri_compressed, detail=1)))
    cprint('JSON SIZE: {}'.format(naturalsize(asizeof.asizeof(js, detail=1))), 'green')
    cprint('OLD JSON SIZE: {}'.format(naturalsize(asizeof.asizeof(js2, detail=1))), 'green')
    cprint('Compression took: {:f}s'.format(t2-t1), 'blue')
    q.put(js2)



# def cache_file(path, file, time_zero):
#     start_time = time.time()
#     cprint('\n======= processing file {}...'.format(file), color='blue')
#     f = open(os.path.join(path, file), 'rU', encoding='utf-8')
#     raw = f.read()
#     f.close()

#     tokens = nltk.word_tokenize(raw)
#     book = nltk.Text(tokens)
#     hapaxes = len(nltk.probability.FreqDist(
#         book).hapaxes()) / len(set(book))
#     vocab_count = len(set(book))
#     print(
#         '=== {:.2f}s -- Text class initialized'.format(time.time() - start_time))

#     # bigrams = nltk.bigrams(book)
#     bi_cfd = nltk.ConditionalFreqDist(bigrams(book))
#     print('=== {:.2f}s -- bigrams done'.format(time.time() - start_time))

#     # trigrams = nltk.utils.trigrams(book)
#     tri_cfd = nltk.ConditionalFreqDist(((x, y), z) for x, y, z in trigrams(book))
#     print('=== {:.2f}s -- trigrams done'.format(time.time() - start_time))

#     file_dict = {'bigrams': bi_cfd, 'trigrams': tri_cfd}
#     # cache_dict['{}'.format(file)] = file_dict
#     # cache_dict['{}'.format(file)].update(
#     #     {'hap': hapaxes, 'v_count': vocab_count})
#     cprint('====== {:.2f}s -- cached {}\n======= total time: {:.2f}s'.format(time.time() -
#                                                 start_time, file, time.time() - time_zero), color='green')

#     return file_dict, hapaxes, vocab_count


# def generate_cache(path, files):
#     cache_dict = {}
#     time_zero = time.time()
#     for file in files:
#         cmd = 'python cache.py {} {}'.format(path, file)
#         ret = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
#         return ret
#         # file_dict, hapaxes, vocab_count = cache_file(path, file, time_zero)
#         # cache_dict['{}'.format(file)] = {}
#         # cache_dict['{}'.format(file)].update(file_dict)
#         # cache_dict['{}'.format(file)].update(
#         #     {'hap': hapaxes, 'v_count': vocab_count})
#         # cprint('====== {:.2f}s -- cached {}\n======= total time: {:.2f}s'.format(time.time() -
#         #                                             start_time, file, time.time() - time_zero), color='green')


#     cprint('\n\n=========== CACHE TOOKED {:.2f} seconds\n =========='.format(
#         time.time() - time_zero), color='yellow')
#     return cache_dict

# # if __name__ == '__main__':
# #     if len(sys.argv)==3:
# #         sys.stdout.write(cache_file(sys.argv[1], sys.argv[2]))
# #         # cache_file(sys.argv[1], sys.argv[2])