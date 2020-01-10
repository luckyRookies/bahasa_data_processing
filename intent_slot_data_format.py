# -*- coding: utf-8 -*-
import os
import json
import re
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
loger = logging.getLogger(__name__)


def split_punctuation(sentence):
    s1 = ' '.join(re.sub(r'([\w])([,.!?])([^\w])', r'\1 \2 \3 ', sentence).split())
    # process the end of line
    return ' '.join(re.sub(r'([\w])([,.!?])$', r'\1 \2 ', s1).split())

def delete_punctuation(sentence):
    s1 = ' '.join(re.sub(r'([\w])([,.!?])([^\w])', r'\1 \3', sentence).split())
    # process the end of line
    return ' '.join(re.sub(r'([\w])([,.!?])$', r'\1', s1).split())

def test_split():
    s_l = ['baik, silahkan anda membayar melalui BCA dinomor 25625252 a.n ana sebesar 50.000'
        , 'Siapkan dirimu menyambut Industri 4.0. Ikuti Kompetisi IT membuat Aplikasi Mobile dengan total hadiah IDR 11juta! Dapatkan juga info eksklusif dari Tim Akademik Fakultas Bisnis, Teknik & IT, University of Technology of Sydney.'
        , 'saya ingin mengikuti workshop industri 4.0. apakah anda bisa memberi saya beberapa informasi?'
        , 'workshop ya???'
        , 'bisa tidak via ovo dan dana/'
        , '08:00.'
        , '20.000 - 100.000'
        , 'tersedia, anda dapat ke website www.tiket.com'
        , 'ada seminar/pelatihan'
        , 'akan dikenakan sebesar 110,000 per orang'
        , 'acara berlangsung tanggal 14-15 september, mulai pukul 15.00 sampai pukul 23.00']
    for s in s_l:
        print(split_punctuation(s))
        print(s)


def format_data():
    dir_list = ['hotel', 'attraction', 'taxi', 'restaurant']
    # dir_list = ['attraction']
    output_dir = 'formatted_data/bahasa'
    bahasa_domain_intent_sents = {}
    for d in dir_list:
        all_sent = set()
        all_intents = set()
        all_slots = set()
        intent_sents = {}

        for parent, dirs, files in os.walk(d):
            print('scanning directory: {}'.format(parent))
            for f in files:
                filepath = os.path.join(parent, f)
                print('scanning file:', filepath)
                # print('filepath: {}'.format(filepath))
                with open(filepath, 'r', encoding='utf8') as fd:
                    data = json.load(fd)
                    for chat_msg in data['chatMessages']:
                        print('-' * 10 + 'begin of chat Message' + '-' * 10)

                        # pre-process raw message
                        raw_msg = chat_msg['message']
                        processed_msg = split_punctuation(raw_msg)
                        print('raw msg:', raw_msg)
                        print('pro msg:', processed_msg)

                        # add {action: [sentence]}
                        # actions = map(lambda tup: tup[0], filter(lambda tup: tup[1] == True, chat_msg['action'].items()))
                        # for act in actions:
                        #     if act not in action_sents:
                        #         action_sents[act] = set()
                        #     action_sents[act].add(processed_msg)

                        # get intent sorted by index
                        intent_fil = filter(lambda tup: tup[1] != False, chat_msg['intent'].items())
                        intent_res = list(map(lambda tup: tup[0], sorted(intent_fil, key=lambda tup: tup[1]['index'])))
                        if len(intent_res) == 0:
                            intent = '<NULL>'
                        else:
                            intent = ';'.join(intent_res)
                        print('intent: {}'.format(intent))

                        # get slots
                        indices = []
                        tokens = []
                        start_index = 0
                        for i in range(len(processed_msg)):
                            if processed_msg[i].isspace():
                                tokens.append(processed_msg[start_index: i])
                                indices.append(start_index)
                                start_index = i + 1
                        tokens.append(processed_msg[start_index:])
                        indices.append(start_index)

                        # print('intent :', intent)
                        print('tokens :', tokens)
                        print('indices:', indices)

                        # init slots and fill slot tags
                        slots = ['O']*len(tokens)
                        slotsList = chat_msg['slotsList']
                        flag_pass = True
                        for slot in slotsList:
                            begin = slot['begin']
                            end = slot['end']
                            text_punc = delete_punctuation(slot['text'])
                            slot_name = slot['templatesNames'][0]

                            print('slot text:', text_punc)
                            print('slot name:', slot_name)
                            # if len(slot_name) == 1:
                            #     slot_name = slot_name[0]
                            # print(text_tokens)
                            try:
                                text_index = processed_msg.index(text_punc, max(0, begin-3))
                            except ValueError:
                                try:
                                    text_index = processed_msg.index(text_punc, 0)
                                except ValueError:
                                    # delete data with punctuation in middle of sentence
                                    flag_pass = False
                                    print('|'*20)
                                    print('Deleted: slot text with punctuation in middle of sentence')
                                    # print('pro message:', processed_msg)
                                    # print('raw message:', raw_msg)
                                    print('raw token: {}, begin:{}'.format(slot['text'], begin))
                                    print('|'*20)
                                    break
                            text_tokens = delete_punctuation(slot['text']).split()
                            for tti in range(len(text_tokens)):
                                ti = processed_msg.index(text_tokens[tti], text_index)
                                text_index += len(text_tokens[tti]) + 1   # avoid text token appear more then once in text
                                if tti == 0:
                                    t_slot_name = 'B-' + slot_name
                                else:
                                    t_slot_name = 'I-' + slot_name
                                try:
                                    slots[indices.index(ti)] = t_slot_name
                                    # add slot class tag
                                    all_slots.add(t_slot_name)
                                except ValueError:
                                    '''
                                    can not find token index
                                    eg: 
                                        sentence: mulai jam15:00 sampai jam 23:00
                                        tokens: ['mulai', 'jam15:00', 'sampai', 'jam', '23:00']
                                        indices: [0, 6, 15, 22, 26]
                                        text token: 15:00
                                        text index: 9 (not in indices raise exception)
                                    '''
                                    print('>' * 20)
                                    # print(tokens)
                                    # print(indices)
                                    # print(processed_msg)
                                    print('Break: can not find slot token index in indices')
                                    print('slot token:', text_tokens[tti], 'slot token index:', ti)
                                    print('<'*20)
                                    break
                        print('Final result: ', '#'*10)
                        # print('tokens:', tokens)
                        print('slots:', slots)
                        print('intent:', intent)

                        if flag_pass:
                            # add data
                            sent = ' '.join([t+':'+s for (t, s) in zip(tokens, slots)]) + ' <=> ' + intent
                            print('sentence:', sent)
                            all_sent.add(sent)

                            if len(intent_res) != 0:
                                all_intents.update(intent_res)
                                for i in intent_res:
                                    if i not in intent_sents:
                                        intent_sents[i] = set()
                                    intent_sents[i].add(processed_msg)
                            else:
                                null_intent = '<NULL>'
                                all_intents.add(null_intent)
                                if null_intent not in intent_sents:
                                    intent_sents[null_intent] = set()
                                intent_sents[null_intent].add(processed_msg)

        # init domain intent sentence dict
        if d not in bahasa_domain_intent_sents:
            bahasa_domain_intent_sents[d] = {i: list(s) for i,s in intent_sents.items()}

        '''
        flush domain data to file
        '''

        print('*'*20)
        print('all sentences:', len(all_sent))
        print(len(all_slots))
        print(len(all_intents))
        print(intent_sents.keys())
        if not os.path.exists(os.path.join(output_dir, d)):
            os.makedirs(os.path.join(output_dir, d))
        with open(os.path.join(output_dir, d, 'data'), 'w', encoding='utf8') as fd:
            fd.writelines([s + '\n' for s in all_sent])
        with open(os.path.join(output_dir, d, 'vocab.intent'), 'w', encoding='utf8') as fd:
            fd.writelines(sorted([s + '\n' for s in all_intents]))
        with open(os.path.join(output_dir, d, 'vocab.slot'), 'w', encoding='utf8') as fd:
            fd.writelines(sorted([s + '\n' for s in all_slots]))

    # sentences of same intent save to file
    with open(os.path.join('formatted_data', 'bahasa_domain_intent_sents.json'), 'w', encoding='utf8') as fd:
        json.dump(bahasa_domain_intent_sents, fd)




if __name__ == '__main__':
    format_data()
    # test_split()