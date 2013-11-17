from copy import copy
from itertools import imap
from word_list import WordList

__author__ = 'brentpayne'


class PhraseDictionary(dict):
    """
    The phrase dictionary contains sequences of identified phrases as a sequence of tokens.  It can be used to convert
    a string of tokens into a phrase id.  Phrase ids
    """

    def __init__(self, phrases=None, word_list=None):
        self.id2phrase = {}
        self.phrase_id_gen = self.phrase_id_generator()
        self.word_list = word_list if word_list else WordList()
        if phrases:
            map(self.add_phrase, phrases)

    def phrase_id_generator(self):
        """
        A generator for automatically labeling the next added phrase.
        Phrase IDs are negative by convention, as Word IDs are positive by convention.
        This is make it easy to extend and mix word ids and phrase ids without using the class system.
        :return: the next negative phrase ID
        """
        id = 0
        while True:
            id -= 1
            yield id


    def add_phrase(self, phrase, id=None):
        """
        Adds a new phrase to the dictionary
        :param phrase: the new phrase as a list of tokens
        :param phrase_id: optionally the phrase_id can be set on addition.  Beware, if you set one id you should set
            them all as the auto-generated ids do not take into account phrase_ids set this way.
        :return: None
        """
        phrase_id = id if id is not None else self.phrase_id_gen.next()
        PhraseDictionary._add_phrase(copy(phrase), phrase_id, self, self.word_list)
        self.id2phrase[phrase_id] = phrase

    @classmethod
    def _add_phrase(cls, phrase, phrase_id, dictionary=None, word_list=None):
        """
        Adds a phrase to a phrase dictionary.
        :param phrase: list of tokens
        :param phrase_id: phrase id
        :param dictionary: phrase dictionary
        :return: new phrase dictionary
        """
        # @Note: this function is called recursively
        if dictionary is None:
            dictionary = {}
        if len(phrase):
            current_word = phrase.pop(0)  # return the first word and remove it from the list
            # if word_list is not None and current_word not in word_list: #@TODO remove, words should already be ids
            #     word_list.add(current_word)
            if current_word not in dictionary:
                dictionary[current_word] = {}
            cls._add_phrase(phrase, phrase_id, dictionary[current_word], word_list)
        else:
            dictionary[None] = phrase_id
        return dictionary

    def contains(self, id):
        """
        Determines if an ID is part of the word lis
        :param id: the id to check
        :return: True if the id is in the word list
        """
        return id in self.id2phrase

    def contains_text_tokens(self, text_tokens):
        """
        Returns true if a phrase in the dictionary matches the list of text tokens
        :param text_tokens: a list of tokens.  Each token a string of text.
        :return: True/False
        """
        id_run = []
        for token in text_tokens:
            id = self.word_list.get(token, None)
            if id is None:
                return False  # since a token is not in the word list, the phrase is not in the dictionary
            id_run.append(id)
        return self.contains_tokens(id_run)


    def contains_tokens(self, tokens):
        """
        Returns true if a phrase in the dictionary matches the list of tokens
        :param tokens: a list of token ids.
        :return: True/False
        """
        #if the maximal phrase is the whole id run, then the phrase is in the dictionary
        return PhraseDictionary.return_max_phrase(tokens, 0, self)[1] == len(tokens)


    def get_phrase(self, id):
        """
        Returns the phrase for a given id. If the phrase does not exist it returns None
        :param id: phrase id
        :return: phrase in original format
        """

        return self.id2phrase.get(id, None)

    @staticmethod
    def return_max_phrase(run, idx, dictionary):
        """
        Finds the maximal phrase in the run starting from the given index.  It uses the dictionary to find sequences of ids
         that can be merged into a phrase.
        :param run: a run of ids
        :param idx: the position in the run to start looking for a merge sequence
        :param dictionary: the dictionary to use to determine if a merge id is present.  This should be a dictionary of
        dictionaries.  Each inner dictionary is a continuation of a mergable run.  The end of a run is donated by a None key
        in a dictionary.  The value associated with the None key is the integer of the merge id.
        :return: phrase_id or None, index after the phrase_id or the current index if no phrase was found.
        """
        if idx < len(run) and run[idx] in dictionary:
            id = run[idx]
            rv, idx = PhraseDictionary.return_max_phrase(run, idx+1, dictionary[id])
            if rv is not None:
                return rv, idx

        if None in dictionary:
            return dictionary[None], idx
        else:
            return None, None
