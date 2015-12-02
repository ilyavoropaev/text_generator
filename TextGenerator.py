import os
import pickle
import random


class TextGenerator:
    def __init__(self, statistics_file_path):
        self.path = statistics_file_path

        if os.path.exists(statistics_file_path):
            self.load_statistics()

        else:
            self.title_words = list()
            self.one_word_statistics = dict(dict())
            self.two_words_statistics = dict(dict())
            self.statistics = [self.title_words,
                               self.one_word_statistics,
                               self.two_words_statistics]
            self.dump_statistics()

    def load_statistics(self):
        with open(self.path, 'rb') as f:
            self.statistics = pickle.load(f)
        self.title_words = self.statistics[0]
        self.one_word_statistics = self.statistics[1]
        self.two_words_statistics = self.statistics[2]

    def dump_statistics(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self.statistics, f)
        self.clear_statistics()

    def clear_statistics(self):
        self.title_words = list()
        self.one_word_statistics.clear()
        self.two_words_statistics.clear()
        self.statistics = [self.title_words,
                           self.one_word_statistics,
                           self.two_words_statistics]

    def update(self, directory_path):
        self.load_statistics()
        cnt = 0
        for text_file_path in os.listdir(directory_path):
            cnt += 1
            print '{} out of {}'.format(cnt, len(os.listdir(directory_path)))
            with open(directory_path + text_file_path) as f:
                text = f.read()
                clean_text = text.replace('-', ' ').replace('.', ' . ').\
                    translate(None, ',:;"!?#^%&*(\)]')

                # remove non-printable characters and split to words
                words = ''.join([i if ord(i) < 128 else ' ' for i in clean_text]).split()

                for i in range(len(words) - 2):
                    # update title_words list
                    if words[i].istitle() and words[i] not in self.title_words:
                        self.title_words.append(words[i])
                        words[i].lower()

                    # update one_word_statistics dict
                    if words[i] in self.one_word_statistics:
                        if words[i + 1] in self.one_word_statistics[words[i]]:
                            self.one_word_statistics[words[i]][words[i + 1]] += 1
                        else:
                            self.one_word_statistics[words[i]][words[i + 1]] = 1
                    else:
                        self.one_word_statistics[words[i]] = {words[i + 1]: 1}

                    # update two_words_statistics dict
                    current_two_words = words[i] + ' ' + words[i + 1]
                    if current_two_words in self.two_words_statistics:
                        if words[i + 2] in self.two_words_statistics[current_two_words]:
                            self.two_words_statistics[current_two_words][words[i + 2]] += 1
                        else:
                            self.two_words_statistics[current_two_words][words[i + 2]] = 1
                    else:
                        self.two_words_statistics[current_two_words] = {words[i + 2]: 1}

        self.dump_statistics()

    def generate_title_word(self):
        word = self.title_words[random.randrange(0, len(self.title_words))]
        while self.generate_second_word(word) == '.':
            word = self.title_words[random.randrange(0, len(self.title_words))]
        return word

    def generate_second_word(self, word):
        return self.one_word_statistics[word].items()[-1][0]

    def generate_word(self, first_word, second_word):
        word = first_word + ' ' + second_word
        return self.two_words_statistics[word].items()[-1][0]

    def generate_chapter(self, paragraphs_in_chapter, chapter_number):
        paragraphs = 0
        chapter = ''
        title = '\n\nChapter ' + str(chapter_number) + '. '
        first_word = self.generate_title_word()
        title += first_word + ' '
        for i in range(random.randrange(2, 4)):
            second_word = self.generate_second_word(first_word)
            title += second_word.title() + ' '
            first_word = second_word
        title += '\n\n\n'
        chapter += title

        while paragraphs < paragraphs_in_chapter:
            paragraphs += 1
            sentences_in_paragraph = random.randrange(4, 10)
            chapter += self.generate_paragraph(sentences_in_paragraph)
        return chapter, title

    def generate_paragraph(self, sentences_in_paragraph):
        # print 'par'
        sentences = 0
        paragraph = '\t'
        while sentences < sentences_in_paragraph:
            paragraph += self.generate_sentence()
            sentences += 1
        paragraph += '\n\n'
        return paragraph

    def generate_sentence(self):
        # print 'sen'
        sentence = ''
        first_word = self.generate_title_word()
        sentence += first_word + ' '

        second_word = self.generate_second_word(first_word)
        sentence += second_word

        current_word = self.generate_word(first_word, second_word)
        num = 0
        while current_word != '.' and num < 20:
            num += 1
            sentence += ' ' + current_word
            first_word = second_word
            second_word = current_word
            current_word = self.generate_word(first_word, second_word)
        # current_word = '.'
        sentence += '. '
        return sentence

    def generate_text(self, destination_file_path, number_of_words):
        random.seed()
        # self.load_statistics()

        text = ''
        table_of_contents = ''
        chapter_number = 1
        while len(text.split()) < number_of_words:
            paragraphs_in_chapter = random.randrange(15, 25)
            chapter, chapter_title = self.generate_chapter(paragraphs_in_chapter, chapter_number)
            text += chapter
            table_of_contents += chapter_title
            chapter_number += 1

        with open(destination_file_path, 'w') as f:
            f.write('Contents\n\n' + '_' * 60 + table_of_contents + '_' * 60 + '\n' + text)

filename = '/asimov_dickens_pratchett.txt'
test = TextGenerator(os.getcwd() + filename)
# test.update(os.getcwd() + '/TEST/')
test.generate_text(os.getcwd() + '/generated_text.txt', 10000)
# test.update(os.getcwd() + '/asimov/')
# print 'asimov updated'
# test.update(os.getcwd() + '/pratchett/')
# print 'pratchett updated'
# test.update(os.getcwd() + '/dickens/')
# print 'dickens updated'
