#!/usr/bin/env python
import fileinput
import os


dir_path = os.path.dirname(os.path.realpath(__file__))
library = os.path.join(dir_path, '..', 'teksty')
files = [name for name in os.listdir(
    library) if not name.startswith('.')]

outfilename = os.path.join(library, "all_files.txt")


def get_langs(files):
    res = set()
    for file in files:
        res.add(file.split('-')[0])
    return res


def make_merge(outfilename, files):
    with open(outfilename, 'w', encoding="utf-8") as fout, fileinput.input(files) as fin:
        for line in fin:
            fout.write(line)

if __name__ == '__main__':
    for lang in get_langs(files):
        files_to_merge = [file for file in files if file.startswith(lang)]
        outfile = os.path.join(library, lang + '-all.txt')
        os.chdir(library)
        make_merge(outfile, files_to_merge)
