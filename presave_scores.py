import pickle,math,sys,argparse,shutil,scoriserial
from scoricomb import *

parser = argparse.ArgumentParser(
	prog="scoricomb-presave",
	description="Pre-stores score permutations for faster calculations when finding higher score permutations")
parser.add_argument("max_score")
parser.add_argument("-o", "--output", action="store_const", const="prestored_paths.scoricomb", default="prestored_paths.scoricomb")
parser.add_argument("-s", "--from-scratch", action="store_false",default=False)
parser.add_argument("-C", "--cores", default="2")

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
def safe_dump(dict,fn, exit_attempt=0):
	try:
		scoriserial.write(fn,dict)
		if(exit_attempt == 1):
			raise Exception()
		return exit_attempt
	except KeyboardInterrupt:
		print("Saving file! Won't exit unless you forcibly kill with another task.")
		return safe_dump(dict,fn,exit_attempt=1)
	return 0
def rotate(tarr):
	a=[]
	b=[]
	for t in tarr:
		a.append(t[0])
		b.append(t[1])
	return a,b

def presavev2(fn,max_sqrt=1,max_cores=2):
	dict = {}
	dict = scoriserial.read_all(fn)
	get_prestored(None, dict)
	k=0
	return_val = 0
	for b in range(max_sqrt):
		try:
			for a in range(b,max_sqrt):
				if(str(a)+"-"+str(b) in dict):
					continue
				_,_,_,_,res=subperm(a,b,epat=", processing "+str(a)+"-"+str(b)+", "+str(b*max_sqrt+a)+"/"+str(max_sqrt**2),max_cores=max_cores)
				res=filterdown(res,a,b)
				dict[str(a)+"-"+str(b)] = [list(r) for r in res]
				if(safe_dump(dict, fn)==1):
					return_val=1
					break
				get_prestored(None, dict)
		except KeyboardInterrupt:
			return_val = 1
			break
	dict["6-0"]=[([6],[0]),([3,3],[0,0]),([2,2,2],[0,0,0])]
	dict["7-0"]=[([7],[0]),([3,2,2],[0,0,0])]
	dict["8-0"]=[([8],[0]),([3,3,2],[0,0,0]),([2,2,2,2],[0,0,0,0]),([6,2],[0,0])]
	safe_dump(dict,fn)
	return return_val

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
	safe_dump(dict,fn)
	print("\nAll done!")
	min_score_paths = dict
parsed = parser.parse_args()
if parsed.from_scratch:
	presave(fn=parsed.output,max_vals=12)
for i in range(0,int(parsed.max_score)+1):
	get_prestored(fn=parsed.output)
	if(presavev2(parsed.output,int(parsed.max_score),int(parsed.cores))==1):
		break

