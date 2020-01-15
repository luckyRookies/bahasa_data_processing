# -*- coding: utf-8 -*-
import os
import json
import re
import logging
logging.basicConfig(level=logging.INFO)#,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def format_data():
    dir_list = ['hotel', 'attraction', 'taxi', 'restaurant'] #['hotel']
    bahasa_dir = '../../multiwoz_bahasawoz_v2/bahasa'
    multiwoz_d_i_s_file = '../../multiwoz_bahasawoz_v2/multiwoz_domain_intent_sents.json'
    output_dir = '../../multiwoz_bahasawoz_v2/bahasa_both'
    domain_intent_both = json.load(open('lang_domain_intent_both.json', 'r', encoding='utf8'))
    multiwoz_d_i_s_dict = json.load(open(multiwoz_d_i_s_file, 'r', encoding='utf8'))
    logger.debug('{}'.format(domain_intent_both))

    lang_domain_intent_sens_both = {'bahasawoz': {}, 'multiwoz': {}}


    for d in dir_list:
        d_intents = domain_intent_both[d].values()
        d_ba_intents = [b_e[0] for b_e in d_intents]
        d_en_intents = [b_e[1] for b_e in d_intents]
        logger.debug('{}'.format(d_ba_intents))

        ba_domain_sens = []
        ba_domain_intents = set()
        ba_domain_slots = set()
        ba_domain_intent_sens = {}
        en_domain_intent_sens = {}

        # bahasa domain extract
        with open(os.path.join(bahasa_dir, d, 'data'), 'r', encoding='utf8') as fd:
            for l in fd:
                l = l.strip()
                if l == '':
                    continue
                sentence, intents = l.split(' <=> ')
                intent = intents.split(';')[0]
                # filter intent of both
                if intent in d_ba_intents:
                    ba_domain_sens.append(l)
                    if intent not in ba_domain_intent_sens:
                        ba_domain_intent_sens[intent] = []
                    # convert sentence to raw sentence
                    tokens = []
                    slots = []
                    for t_s in sentence.split(' '):
                        ts_s = t_s.split(':')
                        if len(ts_s) == 2:
                            t, s = ts_s
                        else:
                            t, s = ':'.join(ts_s[:-1]), ts_s[-1]
                        tokens.append(t)
                        slots.append(s)
                    ba_domain_intents.add(intent)
                    ba_domain_slots.update(slots)
                    raw_sen = ' '.join(tokens)

                    logger.debug('sentence: {}\nraw sentence: {}\nintent: {}'.format(sentence, raw_sen, intent))

                    ba_domain_intent_sens[intent].append(raw_sen)
        for intent, sens in ba_domain_intent_sens.items():
            ba_domain_intent_sens[intent] = sorted(set(sens))


        # multiwoz domain extract
        for intent, sens in multiwoz_d_i_s_dict[d].items():
            if intent in d_en_intents:
                en_domain_intent_sens[intent] = sorted(sens)


        # logger.debug('en: {}'.format(en_domain_intent_sens))
        # logger.debug('ba: {}'.format(ba_domain_intent_sens))
        # logger.debug('ba sens: {}'.format(ba_domain_sens))

        # bahasa: extracted data dump to file
        logger.debug('intents: {}\nslots: {}'.format(sorted(ba_domain_intents), sorted(ba_domain_slots)))
        if not os.path.exists(os.path.join(output_dir, d)):
            os.makedirs(os.path.join(output_dir, d))
        with open(os.path.join(output_dir, d, 'data'), 'w', encoding='utf8') as fd:
            fd.writelines([s + '\n' for s in ba_domain_sens])
        with open(os.path.join(output_dir, d, 'vocab.intent'), 'w', encoding='utf8') as fd:
            fd.writelines(sorted([s + '\n' for s in ba_domain_intents]))
        with open(os.path.join(output_dir, d, 'vocab.slot'), 'w', encoding='utf8') as fd:
            fd.writelines(sorted([s + '\n' for s in ba_domain_slots]))

        lang_domain_intent_sens_both['bahasawoz'][d] = ba_domain_intent_sens
        lang_domain_intent_sens_both['multiwoz'][d] = en_domain_intent_sens
    with open('../../multiwoz_bahasawoz_v2/lang_domain_intent_sens_both.json', 'w', encoding='utf8') as fd:
        json.dump(lang_domain_intent_sens_both, fd)
    with open('../../multiwoz_bahasawoz_v2/ba_domain_intent_sens_both.json', 'w', encoding='utf8') as fd:
        json.dump(lang_domain_intent_sens_both['bahasawoz'], fd)
    with open('../../multiwoz_bahasawoz_v2/en_domain_intent_sens_both.json', 'w', encoding='utf8') as fd:
        json.dump(lang_domain_intent_sens_both['multiwoz'], fd)
    # language domian intent sentences both to file







if __name__ == '__main__':
    format_data()