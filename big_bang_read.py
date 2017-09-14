import re

def get_bang_convs():
	fname = 'big_bang.txt'
	convos = []
	char_dict = {}
	with open(fname) as f:
		content = f.readlines()
		for line in content:
			if line[0:6] == 'Scene:':
				convos.append([])
			else:
				idx = line.find(':')
				if idx is not -1:
					char = line[:idx]
					char = re.sub("[\s]*\([\w\s,.\-']*\)[\s]*", '', char)
					changed_line = re.sub('\([\w\s.,]*\)', '', line)
					if char_dict.get(char.strip()) is None:
						char_dict[char.strip()] = [changed_line[idx + 1:].strip()]
					else:
						char_dict[char.strip()].append(changed_line[idx + 1:].strip())
				line = re.sub(r'\([\w\s,.]+\)[.]*', '', line) 
				line = re.sub('([A-Za-z\s,.]+:)','', line)
				if line.strip() is not '' and line[:6] is not 'Credit':
					convos[-1].append(line.strip())
	#print len(char_dict['Sheldon'])
	return convos, char_dict



def get_bang_ques_ans(convos):
	ques, ans = [], []
	for conv in convos:
		for idx, line in enumerate(conv[:-1]):
			ques.append(conv[idx])
			ans.append(conv[idx + 1])
	assert len(ques) == len(ans)
	#print(len(ques))
	return ques, ans

if __name__ == '__main__':
	convos, char_dict = get_bang_convs()
	ques, ans = get_bang_ques_ans(convos)
	ques_out = open('ques.txt', 'w+')
	# for char in char_dict.keys():
	# 	ques_out.write(char + ' ' + str(len(char_dict[char])) + '\n')
   # 	ans_out = open('ans.txt', 'w+')
    	#for question in char_dict.keys():
    	#	ques_out.write(key + '\n')
    	# for answer in ans:
    	# 	ans_out.write(answer)

