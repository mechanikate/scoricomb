import pickle,math,sys,argparse
from scoricomb import *

parser = argparse.ArgumentParser(
	prog="ScoricombPresave",
	description="Pre-stores score permutations for faster calculations when finding higher score permutations")
parser.add_argument("max_score")
parser.add_argument("-o", "--output", action="store_const", const="prestored_paths.pkl", default="prestored_paths.pkl")
parser.add_argument("-s", "--from-scratch", action="store_false",default=False)

score_ways_one_dir = [(2,0),(3,0),(6,0),(6,1),(7,0),(8,0)]
score_ways = [e for e in score_ways_one_dir]
score_ways.extend([e[::-1] for e in score_ways_one_dir])
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

def presavev2(fn,max_sqrt=1):
	dict = {}
	with open(fn, "rb+") as f:
		dict = pickle.load(f)
	k=0
	for b in range(max_sqrt):
		try:
			for a in range(b,max_sqrt):
				if(str(a)+"-"+str(b) in dict):
					continue
				_,_,_,_,res=subperm(a,b,epat=", processing "+str(a)+"-"+str(b)+", "+str(b*max_sqrt+a)+"/"+str(max_sqrt**2))
				res=filterdown(res,a,b)
				dict[str(a)+"-"+str(b)] = [list(r) for r in res]
		except KeyboardInterrupt:
			with open(fn, "wb+") as f:
				pickle.dump(dict, f)
			return 1
	with open(fn, "wb+") as f:
		pickle.dump(dict,f)
	return 0

def presave(fn="prestored_paths.pkl",max_vals=len(score_ways)**6):
	global min_score_paths
	dict = {}
	for i in range(max_vals):
		opts=list(as_base(i))
		opts=[score_ways[int(opt)] for opt in opts]
		a_tallied,b_tallied=rotate(opts)
		label=str(sum(a_tallied))+"-"+str(sum(b_tallied))
		if(label not in dict):
			dict[label]=[]
		dict[label].append((a_tallied,b_tallied))
		print("completed "+label+", "+str(i)+"/"+str(max_vals), end="\r")
	print("Dumping to pickle                        ", end="\r")
	with open(fn, "wb+") as f:
		pickle.dump(dict,f)
	print("\nAll done!")
	min_score_paths = dict
parsed = parser.parse_args()
if parsed.from_scratch:
	presave(fn=parsed.output,max_vals=12)
for i in range(0,int(parsed.max_score)+1):
	get_prestored(fn=parsed.output)
	if(presavev2(parsed.output,int(parsed.max_score))==1):
		break

