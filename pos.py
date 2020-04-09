import warnings
warnings.filterwarnings("ignore")
import sys
import os
target = ""
in_file="NLP6320_POSTaggedTrainingSet-Unix.txt"
total_words = 0
word_dict = dict()
bigram_dict= dict()
max_prob =  0

def parse_file():
    global vocab_count
    global total_words
    with open(in_file) as fp:
        lines = fp.readlines()
    for line in lines:
        line = "<s>_ " + line + " </s>_"
        words = line.split()
        for word in words:
            tokens = word.split("_")
            val = 1
            if tokens[0] == "<s>" or tokens[0] == "</s>":
                tokens[0] = "_tag_"+ tokens[0]
            if tokens[0] in word_dict:
                val += word_dict[tokens[0]]
            word_dict.update({tokens[0]:val})
            total_words += 1
            val = 1
            if tokens[1] == "":
                continue
            if "_tag_" + tokens[1] in word_dict:
                val += word_dict["_tag_" + tokens[1]]
            word_dict.update({"_tag_" + tokens[1]:val})
            total_words += 1

    o_file = open("word_count.txt", "w")
    for key, value in word_dict.items():
        if key is not "":
            o_file.write(str(key+": " + str(value)))
            o_file.write("\n")
    o_file.close()

def create_bigram_model():
    global bigram_dict
    with open(in_file) as fp:
        lines = fp.readlines()
        for line in lines:
            line = "<s>_ " + line[:-1] + " </s>_"
            words = line.split()
            prev = ""
            for word in words:
                tokens = word.split("_")
                if tokens[0] == "<s>":
                    prev = "_tag_<s>"
                elif tokens[0] == "</s>":
                    val = 1
                    if prev not in bigram_dict:
                        bigram_dict.update({prev:dict()})
                    if "_tag_</s>" in bigram_dict[prev]:
                        val += bigram_dict[prev]["_tag_</s>"]
                    else:
                        bigram_dict[prev].update({"_tag_</s>":dict()})
                    bigram_dict[prev].update({"_tag_</s>":val})
                else:
                    if prev != "":
                        val = 1
                        tokens[1] = "_tag_" + tokens[1]
                        if prev not in bigram_dict:
                            bigram_dict.update({prev:dict()})
                        if tokens[1] in bigram_dict[prev]:
                            val += bigram_dict[prev][tokens[1]]
                        bigram_dict[prev].update({tokens[1]:val})

                        val = 1
                        if tokens[1] not in bigram_dict:
                            bigram_dict.update({tokens[1]:dict()})
                        if tokens[0] in bigram_dict[tokens[1]]:
                            val += bigram_dict[tokens[1]][tokens[0]]
                        bigram_dict[tokens[1]].update({tokens[0]:val})
                        prev = tokens[1]

                        val = 1
                        if tokens[0] not in bigram_dict:
                            bigram_dict.update({tokens[0]:dict()})
                        if tokens[1] in bigram_dict[tokens[0]]:
                            val += bigram_dict[tokens[0]][tokens[1]]
                        bigram_dict[tokens[0]].update({tokens[1]:val})

    o_file = open("bigram_model.txt", "w")
    for key, value in bigram_dict.items():
        if key is not "":
            o_file.write("Previous word \"" + key + "\"\n")
            o_file.write(str(value))
            o_file.write("\n")
    o_file.close()

def cal_pos_prob(words, index, prob_cur, prev, tagged_sentence):
    global max_prob
    status = False
    if index == (len(words)):
        return True

    word = words[index]
    prob1 = 0.0
    prob2  = 0.0
    back_track = False
    if word == "_tag_</s>":
        bigram_dict.update({"_tag_</s>":dict()})
        bigram_dict["_tag_</s>"].update({"_tag_</s>":0})
    if word in bigram_dict:
        for key, value in bigram_dict[word].items():
            temp_prob = 0.0
            if key in word_dict and word != "_tag_</s>":
                prob1 = float(value)/float(word_dict[key])
            if prev in bigram_dict and key in bigram_dict[prev]:
                prob2 = float(bigram_dict[prev][key])/float(word_dict[prev])
            if word == "_tag_</s>":
                temp_prob = prob2
            else:
                temp_prob = prob1 * prob2
            prob1 = 0.0
            prob2  = 0.0
            prob_cur *= temp_prob
            #print("Cur_prob:"+str(prob_cur))
            #prev = key
            status = cal_pos_prob(words, index + 1, prob_cur, key, tagged_sentence)
            if status == True:
                back_track = status
            if status is True:
                if index == (len(words) - 1):
                    if prob_cur > max_prob:
                        '''
                        print("Arg max at this moment:",tagged_sentence)
                        print("max probability:",max_prob)
                        '''
                        max_prob = prob_cur
                        del tagged_sentence[:]
                    else:
                        status = False
                        back_track = False
                #print("max:",max_prob)
            if status == True and index != (len(words) - 1):
                #print(tagged_sentence)
                tagged_sentence.append(word + key)
            
            if temp_prob != 0.0:
                prob_cur /= temp_prob
            #print("rewind "+word+":"+str(prob_cur))
    return back_track

def bigram_probability():
    print("POS tagging with the highest probablity:")
    global target
    target = "<s> " + target + " </s>"
    words = target.split()
    prob_cur = 1.0
    prev = "_tag_<s>"
    words[0] = "_tag_" + words[0]
    words[len(words) - 1] = "_tag_" + words[len(words) - 1]
    tagged_sentence = list()
    cal_pos_prob(words, 1, prob_cur, prev, tagged_sentence)
    tagged_sentence.reverse()
    print(tagged_sentence)
    print("Probability of this tagging: ", max_prob)
    return

if __name__ == "__main__":
    target = raw_input("Input Sentence:\n")
    parse_file()
    create_bigram_model()
    bigram_probability()
