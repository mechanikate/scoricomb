import os,json
def getline(fn, line_number, default_to="[-1]"):
	with open(fn, "r") as f:
		for i, line in enumerate(f):
			if i-1 == line_number:
				return line
		return default_to
def setline(fn, line_number, set_to):
	data=[]
	with open(fn, "r") as f:
		data=f.readlines()
	needed = max(3+line_number-len(data),0)
	for i in range(needed):
		data.append("[-1]\n")
	data[line_number+2]=set_to+"\n"
	with open(fn, "w+") as f:
		f.writelines(data)
def to_line_number(a,b,max_a,max_b):
	return (max_a)*a+b
def read(fn, a_score, b_score, default_to="[-1]"):
	json_str = default_to
	with open(fn, "r") as f:
		max_a_score, max_b_score=read_max_size(fn)
		if(a_score <= max_a_score or b_score <= max_b_score):
			json_str = getline(f, to_line_number(a,b,max_a_score,max_b_score))
	return json.loads(json_str)
def read_all(fn):
	if(not os.path.isfile(fn)):
		return {}
	max_a, max_b = read_max_size(fn)
	dict={}
	for a in range(max_a):
		for b in range(max_b):
			key=str(a)+"-"+str(b)
			dict[key] = get_score(fn, a, b, max_a, max_b)
			if(dict[key] == [-1]):
				del dict[key]
	return dict
def read_max_size(fn):
	max_a_score = 0
	max_b_score = 0
	try:
		with open(fn, "r") as f:
			max_scores_raw=f.readline().strip("\n").split("-")
			max_a_score, max_b_score=(int(max_scores_raw[0]), int(max_scores_raw[1]))
	except:
		pass
	return max_a_score+1, max_b_score+1
def write(fn, dict, a_max=0, b_max=0):
	score_labels = list(dict.keys())
	if(a_max == 0 and b_max == 0):
		for e in score_labels:
			a_max=max(a_max,int(e.split("-")[0]))
			b_max=max(b_max,int(e.split("-")[1]))
	a_max = max(a_max,b_max)
	b_max = a_max
	file_thus_far=""
	with open(fn, "w+") as f:
		f.write(str(a_max)+"-"+str(b_max)+"\n")
		for a in range(a_max+1):
			for b in range(b_max+1):
				key = str(a)+"-"+str(b)
				value = "[-1]"
				if key in dict:
					value = json.dumps([list(v) for v in dict[key]])
				f.write(value+"\n")

def set_score(fn,a,b,arr,max_a_score=0,max_b_score=0):
	if(max_a_score == 0 and max_b_score == 0):
		max_a_score, max_b_score = read_max_size(fn)
	if(not os.path.exists(fn)):
		write(fn,{str(a)+"-"+str(b): arr})
	line_number = to_line_number(a,b,max_a_score,max_b_score)
	setline(fn, line_number, json.dumps(arr))
def get_score(fn,a,b, max_a_score = -1, max_b_score = -1):
	if(max_a_score == -1 or max_b_score == -1):
		max_a_score, max_b_score = read_max_size(fn)
	line_number = to_line_number(a,b,max_a_score,max_b_score)
	return json.loads(getline(fn, line_number))
if __name__ == "__main__":
	write("hello_world.scoricomb", {"6-0": [([6],[0]),([3,3],[0,0]),([2,2,2],[0,0,0])]})
	set_score("hello_world.scoricomb", 2, 0, [([2],[0])])
