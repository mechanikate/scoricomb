import json

score_ways_one_dir = [(2,0),(3,0),(6,0),(6,1),(7,0),(8,0)]
score_ways = [e for e in score_ways_one_dir]
score_ways.extend([e[::-1] for e in score_ways_one_dir])
max_scores = 20
def as_base(n, b=len(score_ways)):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]

def rotate(tarr):
	a=[]
	b=[]
	for t in tarr:
		a.append(t[0])
		b.append(t[1])
	return a,b
def presave(f,max_vals=len(score_ways)**6):
	dict = {}
	for i in range(max_vals):
		opts=list(as_base(i))
		opts=[score_ways[int(opt)] for opt in opts]
		a_tallied,b_tallied=rotate(opts)
		label=str(sum(a_tallied))+"-"+str(sum(b_tallied))
		if(label not in dict):
			dict[label]=[]
		dict[label].append([a_tallied,b_tallied])
		print("completed "+label+", "+str(i)+"/"+str(max_vals), end="\r")
	print("Dumping to json                        ", end="\r")
	json.dump(dict,f)
	print("\nAll done!")

with open("prestored_paths.json","w+") as f:
	presave(f,int(input("Presave count:")))


