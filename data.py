from __future__ import print_function
import os
import random
import re
import numpy as np
import config
from big_bang_read import get_bang_convs, get_bang_ques_ans

#returns id2line: a dictionary of identifier to line without \n at end from movie_lines.txt
# ex id2line = {'L1045': 'They do not!', 'L1044': 'They do too!'}
def get_lines():
    id2line = {}
    file_path = os.path.join(config.DATA_PATH, config.LINE_FILE)
    with open(file_path, 'rb') as f:
        lines = f.readlines()
        for line in lines:
            parts = line.split(' +++$+++ ')
            if len(parts) == 5:
                if parts[4][-1] == '\n': #cut off /n at end of line
                    parts[4] = parts[4][:-1]
                id2line[parts[0]] = parts[4]
    return id2line

def get_convos():
    """ Get conversations from the raw data """
    # returns array of arrays with line data from movie_conversations.txt
    # ex. convos = [['L194', 'L195', 'L196'], ['L198', L'199']]
    file_path = os.path.join(config.DATA_PATH, config.CONVO_FILE)
    convos = []
    with open(file_path, 'rb') as f:
        for line in f.readlines():
            parts = line.split(' +++$+++ ')
            if len(parts) == 4:
                convo = []
                for line in parts[3][1:-2].split(', '):
                    convo.append(line[1:-1])
                convos.append(convo)

    return convos

def question_answers(id2line, convos):
    """ Divide the dataset into two sets: questions and answers. """
    # ex. questions: [index 0'they do not!', 'they do to!', 'i hope so.'...length - 1]
    # ex. answers: [index 1'they do to!', 'i hope so.', 'She okay?'...length]
    questions, answers = [], []
    for convo in convos:
        for idx, line in enumerate(convo[:-1]):
            questions.append(id2line[convo[idx]])
            answers.append(id2line[convo[idx + 1]])
    assert len(questions) == len(answers)
    return questions, answers

def bang_char_ques_ans(char_dict, char):
    questions, answers= [], []
    for index, line in enumerate(char_dict[char]):
        questions.append(char_dict[char][index][0])
        answers.append(char_dict[char][index][1])
    assert len(questions) == len(answers)
    return questions, answers

def prepare_dataset(questions, answers, bang_questions, bang_answers, char_dict):
    #stores questions and answers in training and test files in processed directory
    # create path to store all the train & test encoder & decoder
    make_dir(config.PROCESSED_PATH)
    
    # random convos to create the test set
    #random sample w/o replacement: random.sample(population, k)
    #test_ids: list of ids for test data ex. test_ids = [5, 7003, 2, 49]
    sheldon_questions, sheldon_answers = bang_char_ques_ans(char_dict, 'Sheldon')

    test_ids = random.sample([i for i in range(len(questions))],config.TESTSET_SIZE)
    test_ids2 = random.sample([i for i in range(len(bang_questions))],config.TESTSET_SIZE2)
    test_ids3 = random.sample([i for i in range(len(sheldon_questions))],config.TESTSET_SIZE3)
    #Create 4 files in processed path and an array 'files' that stores their names
    filenames = ['train.enc', 'train.dec', 'test.enc', 'test.dec']
    filenames_bang = ['bang_train.enc', 'bang_train.dec', 'bang_test.enc', 'bang_test.dec']
    filenames_sheldon = ['sheldon_train.enc', 'sheldon_train.dec', 'sheldon_test.enc', 'sheldon_test.dec']

    def prepare_files(file_list, test_ids, questions, answers):
        files = []
        for filename in file_list:
            files.append(open(os.path.join(config.PROCESSED_PATH, filename),'wb'))

        for i in range(len(questions)):
            if i in test_ids:
                #if id # in test, write question to test.enc and answer to test.dec
                files[2].write(questions[i] + '\n')
                files[3].write(answers[i] + '\n')
            else:
                #otherwise, write question to train.enc and answer to test.dec
                files[0].write(questions[i] + '\n')
                files[1].write(answers[i] + '\n')

        for file in files:
            file.close()

    prepare_files(filenames, test_ids, questions, answers)
    prepare_files(filenames_bang, test_ids2, bang_questions, bang_answers)
    prepare_files(filenames_sheldon, test_ids3, sheldon_questions, sheldon_answers)

def make_dir(path):
    """ Create a directory if there isn't one already. """
    try:
        os.mkdir(path)
    except OSError:
        pass

def basic_tokenizer(line, normalize_digits=True):
    #returns words: array of tokens
    """ A basic tokenizer to tokenize text into tokens.
    Feel free to change this to suit your need. """
    #removes <u>, </u>, [, ] from given line
    line = re.sub('<u>', '', line) #re.sub is regex
    line = re.sub('</u>', '', line)
    line = re.sub('\[', '', line)
    line = re.sub('\]', '', line)
    words = []
    #re.compiles a regex into a regex object so match or search can be used
    #python 3: b"" turns string into "bytes literal" which turns string into byte. Ignored in Python 2
    #r string prefix is raw string: '\n' is \,n instead of newline
    _WORD_SPLIT = re.compile(b"([.,!?\"'-<>:;)(])") #includes () for re.split below
    _DIGIT_RE = re.compile(r"\d")
    #strip removes whitespace at beginning and end
    #lowercase string
    for fragment in line.strip().lower().split(): #each of these is a fragment ['you,', 'are', 'here!']
        for token in re.split(_WORD_SPLIT, fragment): #each token splits each fragment i.e. each token in ['here', '!']
            if not token: #if empty array
                continue
            if normalize_digits: #substitutes digits with #
                token = re.sub(_DIGIT_RE, b'#', token)
            words.append(token)
    return words

def build_vocab(filename, filename2, normalize_digits=True):
    #writes vocabulary from training input file to vocab file (either enc or dec) 
    in_path = os.path.join(config.PROCESSED_PATH, filename)
    in_path2 = os.path.join(config.PROCESSED_PATH, filename2)
    out_path = os.path.join(config.PROCESSED_PATH, 'vocab.{}'.format(filename[-3:]))

    vocab = {}
    with open(in_path, 'rb') as f:
        for line in f.readlines():
            for token in basic_tokenizer(line):
                if not token in vocab:
                    vocab[token] = 0
                vocab[token] += 1

    with open(in_path2, 'rb') as f:
        for line in f.readlines():
            for token in basic_tokenizer(line):
                if not token in vocab:
                    vocab[token] = 0
                vocab[token] += 1

    sorted_vocab = sorted(vocab, key=vocab.get, reverse=True)
    with open(out_path, 'wb') as f:
        f.write('<pad>' + '\n')
        f.write('<unk>' + '\n')
        f.write('<s>' + '\n')
        f.write('<\s>' + '\n') 
        index = 4
        for word in sorted_vocab:
            if vocab[word] < config.THRESHOLD:
                with open('config.py', 'ab') as cf:
                    if filename[-3:] == 'enc':
                        cf.write('ENC_VOCAB = ' + str(index) + '\n')
                    else:
                        cf.write('DEC_VOCAB = ' + str(index) + '\n')
                break
            f.write(word + '\n')
            index += 1


def load_vocab(vocab_path):
# returns words: array of words in vocab file and dictionary {word: index in vocab file}
    with open(vocab_path, 'rb') as f:
        words = f.read().splitlines()
    return words, {words[i]: i for i in range(len(words))}

def sentence2id(vocab, line):
    #for each token in line, returns word's ID in vocab or <unk>'s id if not in vocab
    return [vocab.get(token, vocab['<unk>']) for token in basic_tokenizer(line)]

def token2id(data, mode, phase):
    """ Convert all the tokens in the data into their corresponding
    index in the vocabulary. """ 
    #Outputs data in the form of tokens from vocab to processed/(train_or_test)/ids.(enc or dec)
    vocab_path = 'vocab.' + mode
    in_path = data + '.' + mode
    out_path = data + '_ids.' + mode

    _, vocab = load_vocab(os.path.join(config.PROCESSED_PATH, vocab_path))
    in_file = open(os.path.join(config.PROCESSED_PATH, in_path), 'rb')
    out_file = open(os.path.join(config.PROCESSED_PATH, out_path), 'wb')
    
    lines = in_file.read().splitlines()
    for line in lines:
        if mode == 'dec' and phase is not 2: # we only care about '<s>' and </s> in encoder
            ids = [vocab['<s>']]
        else:
            ids = []
        ids.extend(sentence2id(vocab, line))
        # ids.extend([vocab.get(token, vocab['<unk>']) for token in basic_tokenizer(line)])
        if mode == 'dec':
            ids.append(vocab['<\s>'])
        out_file.write(' '.join(str(id_) for id_ in ids) + '\n')

def prepare_raw_data():
#puts questions and answers into processed folder for training and test
    print('Preparing raw data into train set and test set ...')
    id2line = get_lines()
    convos = get_convos()
    bang_convs, char_dict = get_bang_convs()
    bang_questions, bang_answers = get_bang_ques_ans(bang_convs)
    questions, answers = question_answers(id2line, convos)
    prepare_dataset(questions, answers, bang_questions, bang_answers, char_dict)

def process_data():
    #creates test and training files of id's from vocabulary
    print('Preparing data to be model-ready ...')
    build_vocab('train.enc', 'bang_train.enc')
    build_vocab('train.dec', 'bang_train.dec')
    token2id('train', 'enc', 1)
    token2id('train', 'dec', 1)
    token2id('test', 'enc', 1)
    token2id('test', 'dec', 1)
    print('Preparing Big Bang data to be model-ready ....')
    token2id('bang_train', 'enc', 2)
    token2id('bang_train', 'dec', 2)
    token2id('bang_test', 'enc', 2)
    token2id('bang_test', 'dec', 2)
    print('Preparing Sheldon data to be model-ready ....')
    token2id('sheldon_train', 'enc', 3)
    token2id('sheldon_train', 'dec', 3)
    token2id('sheldon_test', 'enc', 3)
    token2id('sheldon_test', 'dec', 3)

def load_data(enc_filename, dec_filename, max_training_size=None):
    #returns data_buckets: For each tuple in BUCKETS from config file, contains an array of 2 arrays: encoded ids and decoded ids
    #ex. data_buckets[0][[[36, 759, 100], [115, 225, 336]], [[27, 42, 86], [13, 350, 425]]]
    #for each bucket in config file, makes sure they are less than max enc and max dec specified in config file
    #so groups sequences with like lengths together
    encode_file = open(os.path.join(config.PROCESSED_PATH, enc_filename), 'rb')
    decode_file = open(os.path.join(config.PROCESSED_PATH, dec_filename), 'rb')
    encode, decode = encode_file.readline(), decode_file.readline()
    data_buckets = [[] for _ in config.BUCKETS]
    #array of arrays, one array for each tuple in config.Buckets
    i = 0
    #encode and decode is a line of id's from vocab
    while encode and decode:
        if (i + 1) % 10000 == 0:
            print("Bucketing conversation number", i)
        #encode_ids and decode_ids are arrays of ids from a line (encode and decode above)
        encode_ids = [int(id_) for id_ in encode.split()]
        decode_ids = [int(id_) for id_ in decode.split()]
        for bucket_id, (encode_max_size, decode_max_size) in enumerate(config.BUCKETS):
            if len(encode_ids) <= encode_max_size and len(decode_ids) <= decode_max_size:
                data_buckets[bucket_id].append([encode_ids, decode_ids])
                break #break when added to appropriate bucket
        encode, decode = encode_file.readline(), decode_file.readline()
        i += 1
    return data_buckets

def _pad_input(input_, size):
    #pads by adding dimensions to make dimensions equal
    return input_ + [config.PAD_ID] * (size - len(input_))

def _reshape_batch(inputs, size, batch_size):
    """ Create batch-major inputs. Batch inputs are just re-indexed inputs
    #batch major means first index of tensor is batch size
    """
    batch_inputs = []
    for length_id in range(size):
        batch_inputs.append(np.array([inputs[batch_id][length_id]
                                    for batch_id in range(batch_size)], dtype=np.int32))
    return batch_inputs


def get_batch(data_bucket, bucket_id, batch_size=1):
    """ Return one batch to feed into the model """
    # only pad to the max length of the bucket
    encoder_size, decoder_size = config.BUCKETS[bucket_id]
    encoder_inputs, decoder_inputs = [], []

    for _ in range(batch_size):
        encoder_input, decoder_input = random.choice(data_bucket)
        # pad both encoder and decoder, reverse the encoder
        encoder_inputs.append(list(reversed(_pad_input(encoder_input, encoder_size))))
        decoder_inputs.append(_pad_input(decoder_input, decoder_size))

    # now we create batch-major vectors from the data selected above.
    #encoder_inputs: array of padded/reversed encoded lines
    batch_encoder_inputs = _reshape_batch(encoder_inputs, encoder_size, batch_size)
    batch_decoder_inputs = _reshape_batch(decoder_inputs, decoder_size, batch_size)

    # create decoder_masks to be 0 for decoders that are padding.
    batch_masks = []
    for length_id in range(decoder_size):
        batch_mask = np.ones(batch_size, dtype=np.float32)
        for batch_id in range(batch_size):
            # we set mask to 0 if the corresponding target is a PAD symbol.
            # the corresponding decoder is decoder_input shifted by 1 forward.
            if length_id < decoder_size - 1:
                target = decoder_inputs[batch_id][length_id + 1]
            if length_id == decoder_size - 1 or target == config.PAD_ID:
                batch_mask[batch_id] = 0.0
        batch_masks.append(batch_mask)
    return batch_encoder_inputs, batch_decoder_inputs, batch_masks

if __name__ == '__main__':
    prepare_raw_data()
    process_data()
