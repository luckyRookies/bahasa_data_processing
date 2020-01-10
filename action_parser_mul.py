# -*- coding: utf8 -*-
import os
import json
# from termcolor import colored
import random
import re



class MultiWOZParser:

    def __init__(self, directory=""):
        """
        Downloads the MultiWOZ-2 data set and stores all the interesting file names.
        This does not load the data into RAM.
        :param directory:
        """
        self.directory = directory

        self.data_file_name = os.path.abspath(
            os.path.join(directory, "data.json")
        )
        self.ontology_file_name = os.path.abspath(
            os.path.join(directory, "ontology.json")
        )
        self.acts_file_name = os.path.abspath(
            os.path.join(directory, "dialogue_acts.json")
        )
        self.testlist_file_name = os.path.abspath(
            os.path.join(directory, "testListFile.json")
        )
        self.vallist_file_name = os.path.abspath(
            os.path.join(directory, "valListFile.json")
        )

        assert os.path.exists(self.data_file_name)
        assert os.path.exists(self.acts_file_name)
        assert os.path.exists(self.testlist_file_name)
        assert os.path.exists(self.vallist_file_name)

        self._data = None
        self._ontology = None
        self._names = None
        self._acts = None
        self._test_list = None
        self._validation_list = None
        self._domain_substitute = None


    @property
    def data(self):
        # Load data on demand
        if self._data is None:
            with open(self.data_file_name, "r") as read_file:
                self._data = json.load(read_file)

        # Return the data
        return self._data

    @property
    def ontology(self):
        # Load data on demand
        if self._ontology is None:
            with open(self.ontology_file_name, "r") as read_file:
                self._ontology = json.load(read_file)

        # Return the data
        return self._ontology

    @property
    def story_names(self):
        if self._names is None:
            self._names = list(self.data)
        return self._names

    @property
    def acts(self):
        # Load data on demand
        if self._acts is None:
            with open(self.acts_file_name, "r") as read_file:
                self._acts = json.load(read_file)

        # Return the data
        return self._acts

    @property
    def validation_list(self):
        # Load data on demand
        if self._validation_list is None:
            with open(self.vallist_file_name, "r") as read_file:
                self._validation_list = read_file.read().split()

        # Return the data
        return self._validation_list

    @property
    def test_list(self):
        # Load data on demand
        if self._test_list is None:
            with open(self.testlist_file_name, "r") as read_file:
                self._test_list = read_file.read().split()

        # Return the data
        return self._test_list

    def split_punctuation(self, sentence):
        s1 = ' '.join(re.sub(r'([\w])([,.!?])([^\w])', r'\1 \2 \3 ', sentence).split())
        # process the end of line
        return ' '.join(re.sub(r'([\w])([,.!?])$', r'\1 \2 ', s1).split())

    def get_action_sentences(self):
        val_domain_list = ['attraction', 'restaurant', 'hotel', 'taxi']
        domain_action_sents = {} #{'attraction': {}, 'restaurant': {}, 'hotel': {}, 'taxi': {}}
        for name, dialog in self.data.items():
            log = dialog['log']
            num_turns = len(log)

            name = name[:-5]

            # story = f'## story_{name}' + '\n'
            # print(colored(f'## story_{name}', 'green'))

            count_usr = 0 # How often the user spoke
            count_wiz = 0 # How often the wizard replied (consecutive actions count as one)

            for step in log:
                text = step['text']
                text = self.split_punctuation(text)
                if len(step['metadata']) == 0:
                    # user turn
                    count_usr += 1
                else:
                    # wizard turn
                    count_wiz += 1

                    # parse wizard action
                    if str(count_wiz) in self.acts[name]:
                        action_list = self.acts[name][str(count_wiz)]

                        if type(action_list) is not dict:
                            if type(action_list) is str and action_list == "No Annotation":

                                continue
                        for base_action, slot_list in action_list.items():
                            if '-' in base_action:
                                domain, action_name = base_action.split('-')
                                domain, action_name = domain.lower(), action_name.lower()
                            else:
                                continue
                            if domain not in domain_action_sents:
                                domain_action_sents[domain] = {}
                            for slot in slot_list:
                                slot_name = slot[0].lower()
                                intent = action_name + '_' + slot_name
                                if intent not in domain_action_sents[domain]:
                                    domain_action_sents[domain][intent] = set()

                                domain_action_sents[domain][intent].add(text)

        output_dir = '../MULTIWOZ2.1'
        fil_domain = {}
        for d in val_domain_list:
            if d in domain_action_sents:
                # print(d, domain_action_sents[d].keys())
                fil_domain[d] = list(domain_action_sents[d].keys())
                # print(fil_domain[d].keys())
        # with open(os.path.join(output_dir, 'multiwoz_domain_intent_sents.json'), 'w', encoding='utf8') as fd:
        #     json.dump(fil_domain, fd)
        print(fil_domain)

        # bahasa intent
        bahasa_dir = '../BahasaWOZ/MULTIWOZ_BAHASA/annotations/formatted_data/bahasa'
        bahasa_domain_intent = {}
        for d in val_domain_list:
            intent_list = []
            with open(os.path.join(bahasa_dir, d, 'vocab.intent'), 'r', encoding='utf8') as fd:
                for l in fd:
                    l = l.strip()
                    if l != '':
                        intent_list.append(l)
            bahasa_domain_intent[d] = intent_list
        all_domain_intent = {'multiwoz': fil_domain, 'bahasawoz': bahasa_domain_intent}
        with open(os.path.join(output_dir, 'en_ba_domain_intent.json'), 'w', encoding='utf8') as fd:
            json.dump(all_domain_intent, fd)



if __name__ == '__main__':
    parser = MultiWOZParser(directory='../MULTIWOZ2.1')
    parser.get_action_sentences()






























