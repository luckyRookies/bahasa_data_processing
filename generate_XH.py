# -*- coding: utf-8 -*-
import os
import json
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)#,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_H(en_ba_nums):
    '''

    :param en_ba_nums: [[num_of_vertex_within_edge1, num_of_vertex_within_edge2, ...], [num_of_other_vertex_within_edge1, num_of_other_vertex_within_edge2, ...]]
    :return: incidence matrix
    '''
    col = en_ba_nums.shape[1]
    en_matrix = []
    ba_matrix = []
    for c in range(col):
        en_num = en_ba_nums[0, c]
        ba_num = en_ba_nums[1, c]
        en_mx = [[1 if i == c else 0 for i in range(col)]] * en_num
        ba_mx = [[1 if i == c else 0 for i in range(col)]] * ba_num
        en_matrix += en_mx
        ba_matrix += ba_mx
    en_matrix += ba_matrix
    return np.array(en_matrix)

def generate_XH():
    lang_domain_intent_sens_both = json.load(open('../../multiwoz_bahasawoz_v2/lang_domain_intent_sens_both.json', 'r', encoding='utf8'))
    lang_domain_intent_both = json.load(open('../../multiwoz_bahasawoz_v2/lang_domain_intent_both.json', 'r', encoding='utf8'))
    dir_list = ['hotel', 'attraction', 'taxi', 'restaurant']
    output_dir = '../../multiwoz_bahasawoz_v2/HG_data'

    for d in dir_list:
        logger.debug('domain: %s' % d)
        en_domain_sens = []
        en_nums = []
        ba_nums = []
        # logger.debug('{}'.format(lang_domain_intent_both))
        for i, ba_en_intents in lang_domain_intent_both[d].items():
            logger.debug('i: {}, ba_en_intents: {}'.format(i, ba_en_intents))
            ba_intent, en_intent = ba_en_intents
            ba_domain_intent_sens = lang_domain_intent_sens_both['bahasawoz'][d][ba_intent]
            en_domain_intent_sens = lang_domain_intent_sens_both['multiwoz'][d][en_intent]
            logger.debug('{}'.format(en_domain_intent_sens[:3]))
            en_nums.append(len(en_domain_intent_sens))
            ba_nums.append(len(ba_domain_intent_sens))

            en_domain_sens += en_domain_intent_sens
        logger.debug('en nums: {}, ba nums: {}'.format(en_nums, ba_nums))

        # dump english sentences into file
        if not os.path.exists(os.path.join(output_dir, d)):
            os.makedirs(os.path.join(output_dir, d))
        with open(os.path.join(output_dir, d, 'en_sentences.txt'), 'w', encoding='utf8') as fd:
            fd.write('\n'.join(en_domain_sens))
        np.save(os.path.join(output_dir, d, 'en_ba_sen_nums_metadata.npy'), np.array([en_nums, ba_nums]))


if __name__ == '__main__':
    nums = np.array([[1,2,3], [4,3,2]])
    print(generate_H(nums))