import multiprocessing as mp
import ntpath
from argparse import ArgumentParser
import glob

CORES = mp.cpu_count() + 2


FORBIDDEN_WORDS = ['is', 'a', 'an', 'at', 'the', 'in', 'on', 'and', 'this',
                   'of', 'by', 'do']


def process(line):
    return set([word.lower() for word in line.split()
                if word.lower() not in FORBIDDEN_WORDS])


def process_wrapper(line_id, file_path_arg):
    with open(file_path_arg, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i != line_id:
                continue
            elif line != '\n':
                # remove the dot from the last word in sentence
                return process(line.replace('.', ''))


def check_item(single_item, lines):
    count = 0
    for line in lines:
        if single_item in line:
            count += 1
    return count


def parse_args():
    """parses command line arguments"""
    parser = ArgumentParser()

    parser.add_argument("-d", "--files_path",
                        type=str,
                        dest="files_path",
                        help="Directory of the files"
                        )

    return parser.parse_args()


def main(args):
    # init objects
    pool = mp.Pool(CORES)
    jobs = []

    files_path = args.files_path

    paths = glob.glob(files_path)

    for file_path in paths:
        print(ntpath.basename(file_path))
        # create jobs
        with open(file_path, encoding='utf-8') as f:
            for ID, current_line in enumerate(f):
                jobs.append(pool.apply_async(process_wrapper,
                                             (ID, file_path,))
                            )

        # wait for all jobs to finish
        line_words = []
        for job in jobs:
            result = job.get()
            if result is not None:
                line_words.append(result)

        # dictionary for words mapping
        words_map = {}

        for check_line in line_words:
            for item in check_line:

                # if item is not in map get the number of lines where it occurs
                if item not in words_map:
                    counter = check_item(item, line_words)

                    # put occurs in map
                    words_map[item] = counter

        # get all values
        values = list(words_map.values())

        # get all keys
        keys = list(words_map.keys())

        # counter for the first word in set
        main_counter = 0

        # all word pairs
        pairs = list()
        for item in keys:
            # counter for second word in pair
            second_counter = main_counter + 1

            # go through that word to the end
            for next_item in keys[main_counter + 1:]:
                # calculate similarity
                similarity = values[main_counter] / (
                            values[main_counter] + values[second_counter])

                # add words pair to the pairs list
                pairs.append([item, next_item, similarity])
                second_counter += 1
            main_counter += 1

        for pair in pairs:
            print(pair)

    # clean up
    pool.close()


if __name__ == "__main__":
    arguments = parse_args()
    main(arguments)
