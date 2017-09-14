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
					changed_line = re.sub('\([\w\s.,]*\)', '', line)
					if char_dict.get(line[:idx]) is None:
						char_dict[line[:idx]] = [changed_line[idx + 1:].strip()]
					else:
						char_dict[line[:idx]].append(changed_line[idx + 1:].strip())
				line = re.sub(r'\([\w\s,.]+\)[.]*', '', line) 
				line = re.sub('([A-Za-z\s,.]+:)','', line)
				if line.strip() is not '' and line[:6] is not 'Credit':
					convos[-1].append(line.strip())
	return convos, char_dict



def get_bang_ques_ans(convos):
	ques, ans = [], []
	for conv in convos:
		for idx, line in enumerate(conv[:-1]):
			ques.append(conv[idx])
			ans.append(conv[idx + 1])
	assert len(ques) == len(ans)
	return ques, ans

if __name__ == '__main__':
	convos, char_dict = get_bang_convs()
	ques, ans = get_bang_ques_ans(convos)
	ques_out = open('ques.txt', 'w+')
   # 	ans_out = open('ans.txt', 'w+')
    	for question in ques:
    		ques_out.write(question + '\n')
   # 	for answer in ans:
   # 		ans_out.write(answer)

