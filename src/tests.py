#!/usr/bin/env python
import os
from cache import cache_file, decode_file
from termcolor import cprint
from pympler import asizeof
from multiprocessing import Process, Queue
from timeit import time
import unittest

from gen import generate_from_text
import coverage


class TestCache(unittest.TestCase):
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # UPLOAD_FOLDER = dir_path + "/teksty"

    def _files(self):
        return sorted([f for f in os.listdir(self.UPLOAD_FOLDER) if not f.startswith('.')], reverse=True)

    def _decode(self):
        for file in self.TEXT_CACHE.keys():
            self.cfd[file] = decode_file(self.TEXT_CACHE[file])
        cprint('== SIZE OF CFD: {}'.format(
            asizeof.asizeof(self.cfd)), 'yellow')

    def _generate(self, file):
        t1 = time.time()
        generate_from_text(file=self.UPLOAD_FOLDER + file,
                           prnt=1, num=3, cache=self.TEXT_CACHE)
        t3 = time.time()
        print('time of cached gen: {:f}'.format(t3 - t1))
        generate_from_text(file=self.UPLOAD_FOLDER + file, prnt=0, num=3,)
        t2 = time.time()
        cprint('TEXT GENERATED: {:f}\n\n'.format(t2 - t1), 'yellow')

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.UPLOAD_FOLDER = dir_path + "/teksty/"
        self.TEXT_CACHE = {}
        self.cfd = {f: None for f in self._files()}

    def test_for_flask(self):
        print()
        for file in self._files():
            t1 = time.time()
            cprint('\n======== Caching {}...'.format(file), color='magenta')
            q = Queue()
            # p = Process(target=cache_file, args=(q, UPLOAD_FOLDER, file))
            cache_file(q, self.UPLOAD_FOLDER, file)
            # p.start()
            file_dict = q.get()
            # print(type(file_dict))
            # print(file_dict)
            self.TEXT_CACHE.update({file: file_dict})
            t2 = time.time()
            cprint('FILE CACHED: {:f}'.format(t2 - t1), 'yellow')
            # try:
            #     t1= time.time()
            #     self._decode()
            #     t2= time.time()
            #     cprint('FILE DECODED: {:f}'.format(t2-t1), 'yellow')
            # except Exception as e:
            #     import traceback; traceback.print_exc();
            #     import ipdb; ipdb.set_trace()  # breakpoint b2ab45ec //
            #     self.fail("Decode failed ({}: {})".format(type(e), e))
            try:
                self._generate(file=file)
            except Exception as e:
                print(self.TEXT_CACHE.keys(), self.cfd.keys())
                # import ipdb; ipdb.set_trace()  # breakpoint b2ab45ec //
                self.fail("Gen failed ({}: {})".format(type(e), e))
        cprint('== SIZE OF CACHE: {}'.format(
            asizeof.asizeof(self.TEXT_CACHE)), 'yellow')
if __name__ == '__main__':

    t1 = time.time()
    cov = coverage.coverage(branch=True)
    cov.erase()
    cov.start()
    import gen
    import cache

    tests = ['TestCache']
    # unittest.main(module='unit_tests', exit=False,
    # verbosity=2, defaultTest=tests)
    try:
        unittest.main(verbosity=2)
    except:
        print('tests failed')
    cov.stop()
    modls = [gen, cache]
    cov.report(modls, ignore_errors=1, show_missing=1)
    cov.html_report(morfs=modls, directory='htmlcov')
    cov.erase()
    t2 = time.time()
    print('\n----- TESTS TOOK: {:.2f} min'.format((t2 - t1) / 60))
