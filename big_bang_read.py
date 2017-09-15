import re

def get_bang_convs():
	fname = 'big_bang.txt'
	convos = []
	char_dict = {}
	with open(fname) as f:
		content = f.readlines()
		for line_index, line in enumerate(content):
			if line[0:6] == 'Scene:':
				convos.append([])
			else:
				idx_before = -10
				idx = line.find(':')
				if line_index > 1:
					idx_before = content[line_index - 2].find(':')
				if idx > -1 and idx_before > -1:
					char = line[:idx]
					char = re.sub("[\s]*\([\w\s,.\-']*\)[\s]*", '', char)
					changed_line = re.sub('\([\w\s.,]*\)', '', line)
					before_scene_flag = False
					if content[line_index - 2][:6] == 'Scene:':
						before_scene_flag = True
					changed_line_before = re.sub('\([\w\s.,]*\)', '', content[line_index - 2])
					if char_dict.get(char.strip()) is None:
						if before_scene_flag:
							char_dict[char.strip()] = [['', changed_line[idx + 1:].strip()]]
						else:
							char_dict[char.strip()] = [[changed_line_before[idx_before + 1:].strip(), changed_line[idx + 1:].strip()]]
					else:
						if before_scene_flag:
							char_dict[char.strip()].append(['', changed_line[idx + 1:].strip()])
						else:
							char_dict[char.strip()].append([changed_line_before[idx_before + 1:].strip(), changed_line[idx + 1:].strip()])
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
	print(len(ques))
	return ques, ans

if __name__ == '__main__':
	convos, char_dict = get_bang_convs()
	ques, ans = get_bang_ques_ans(convos)
	ques_out = open('ques.txt', 'w+')
	ans_out = open('ans.txt', 'w+')
	for item in char_dict['Sheldon']:
		ques_out.write(item[0] + '\n')
		ans_out.write(item[1] + '\n') 
	# print char_dict['Sheldon']
		#ques_out.write(dialogue[0] + '\n')
	# for char in char_dict.keys():
	# 	ques_out.write(char + ' ' + str(len(char_dict[char])) + '\n')
   # 	ans_out = open('ans.txt', 'w+')
    	#for question in char_dict.keys():
    	#	ques_out.write(key + '\n')
    	# for answer in ans:
    	# 	ans_out.write(answer)

