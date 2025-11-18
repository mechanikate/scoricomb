import math,os,gc,sys,pickle,argparse,scoriserial
from multiprocessing import Pool, cpu_count
from functools import reduce
from decimal import Decimal as D
from decimal import getcontext
gc.enable()
parser = argparse.ArgumentParser(
	prog="scoricomb",
	description="Calculates every permutation for plays to get to a NFL score")
parser.add_argument("a")
parser.add_argument("b")
parser.add_argument("-o", "--output", default="")
parser.add_argument("-c", "--cache", action="store_true")
parser.add_argument("-C", "--cores", default="2")
# getcontext().prec = 100 # for higher rarity score calculation precision
score_ways_one_dir = [(2,0),(3,0),(6,0),(6,1),(7,0),(8,0)]
score_ways = [e for e in score_ways_one_dir]
score_ways.extend([e[::-1] for e in score_ways_one_dir])
min_score_paths = {}
def get_prestored(fn="prestored_paths.scoricomb",dict={}):
	global min_score_paths
	if(fn==None):
		min_score_paths=dict
		return
	min_score_paths=scoriserial.read_all(fn)
def add_to_prestored(a,b,perms,fn="prestored_paths.scoricomb"):
	msp={}
	with open(fn, "rb") as f:
		msp=pickle.load(f)
	msp[str(a)+"-"+str(b)]=perms
	with open(fn, "wb") as f:
		pickle.dump(msp,f)
dead_ends = [(0,1),(1,0),(1,1),(2,1),(1,2),(3,1),(1,3),(4,1),(1,4),(5,1),(1,5)]
names={
	(2,0): "Team 1 Safety (2-0)",
	(3,0): "Team 1 Field goal (3-0)",
	(6,0): "Team 1 Touchdown (6-0)",
	(7,0): "Team 1 Touchdown+Extra point (7-0)",
	(8,0): "Team 1 Touchdown+2 point conversion (8-0)",
	(6,1): "Team 1 Touchdown+Defensive safety (6-1)",
	(0,2): "Team 2 Safety (0-2)",
	(0,3): "Team 2 Field goal (0-3)",
	(0,6): "Team 2 Touchdown (0-6)",
	(0,7): "Team 2 Touchdown+Extra point (0-7)",
	(0,8): "Team 2 Touchdown+2 point conversation (0-8)",
	(1,6): "Team 2 Touchdown+Defensive safety (1-6)"
}
total=0
# 1146 7pts
# 834 3pts
# 120 6pts
# 45 8pts
# 16 2pts
# 0 6-1pts
# 2161 total
odds = [D(1),D(0),D(16/2161),D(834/2161),D(0),D(0),D(120/2161),D(1146/2161),D(45/2161)]
def dflatten(li):
	res = []
	for e in li:
		if isinstance(e,list):
			res.extend(dflatten(e))
		else:
			res.append(e)
	return res
def recursion(a,b,paths,ap,bp,lvl,epat,max_cores,final,resultant):
	ap,bp,pprev,fls,finl=subperm(a, b, paths, ap, bp, lvl=lvl, epat=epat, max_cores=max_cores)
	final = finl
	resultant = []
	if(fls[1]==0):
		final.append((ap,bp))
	if(fls[0]==0):
		resultant.append((ap,bp))
	return final,resultant
def max_time(a,b):
	return len(score_ways)**(a//2+b//2)
def subperm(a,b,paths=[],a_path=[],b_path=[],flags=[0,0,0],lvl=0,epat="",max_cores=2):
	global total
	final,resultant=([],[])
	total+=1
	#if(total % 255 == 0):
	print(total, end=epat+"\r")
	if(a<0 or b<0 or (a,b) in dead_ends):
		return [0],[0],paths,[1,1,flags[2]],final
	p=str(a)+"-"+str(b)
	p_rev=str(b)+"-"+str(a)
	keysv=list(min_score_paths.keys())
	if p in keysv: # get endings if we're low enough
		for path_sub in min_score_paths[p]:
			a_path_clone=a_path.copy()
			b_path_clone=b_path.copy()
			a_path_clone.extend(path_sub[0])
			b_path_clone.extend(path_sub[1])
			final.append((a_path_clone,b_path_clone))
		return a_path,b_path,paths,[0,0,flags[2]],final
	elif p_rev in keysv:
		for path_sub in min_score_paths[p_rev]:
			a_path_clone=a_path.copy()
			b_path_clone=b_path.copy()
			a_path_clone.extend(path_sub[1])
			b_path_clone.extend(path_sub[0])
			final.append((a_path_clone,b_path_clone))
		return a_path,b_path,paths,[0,0,flags[2]],final
	recursion_fs=[]
	arglist=[]
	if(lvl == 0):
		pool = Pool(processes=max_cores)
		for i,p in enumerate(score_ways): # get rest of paths
			arglist.append((a-p[0],b-p[1],paths,a_path+[p[0]],b_path+[p[1]],lvl+1,epat,max_cores,final,resultant))
		res_tuple = pool.starmap(recursion,arglist)
		for finall,resultantt in res_tuple:
			final.extend(finall)
			resultant.extend(resultantt)
	else:
		for p in score_ways:
			finall,resultantt=recursion(a-p[0],b-p[1],paths,a_path+[p[0]],b_path+[p[1]],lvl+1,epat,max_cores,final,resultant)
			final.extend(finall)
			resultant.extend(resultantt)
	for r in resultant:
		if(sum(r[0]) == a and sum(r[1]) == b):
			paths.append((a_path+[p[0]], b_path+[p[1]]))
	if(lvl > 0):
		return a_path, b_path, paths, [0,1,flags[2]], final
	print(str(a)+"-"+str(b)+": Found "+str(len(final))+" base permutations                               ")
	total=0
	return [],[],paths,[2,2],final

def remove_vals(arr,removables=[[]]):
	f=[]
	for a in arr:
		if(isinstance(a,list)):
			f.append(remove_vals(a,removables))
		if(a in removables):
			continue
		f.append(a)
	return f
def filterdown(res,av,bv):
	newres,seen_a,seen_b=([],set(),set())
	include=[]
	for i,v in enumerate(res):
		condition = True
		try:
			condition = len(v)!=2 or len(v[0])==0 or len(v[1])==0 or (sum(v[0]) != av or sum(v[1]) != bv)
		except Exception as e:
			pass
		if(condition):
			continue
		vc0=sorted(v[0])
		vc1=sorted(v[1])
		a,b = tuple(vc0), tuple(vc1)
		if(a not in seen_a or b not in seen_b):
			seen_a.add(tuple(sorted(a)))
			seen_b.add(tuple(sorted(b)))
			include.append(i)
	return [res[i] for i in include]
def pretty_print(scorelist):
	return "\n".join([names[e] for e in tuple(zip(*scorelist))[::-1]])
def perm(a,b,fn="prestored_paths.pkl",results_fn="",max_cores=2,out_file_pattern="permutations_{a}-{b}.txt",cache_results=True):
	global total
	_,_,_,_,res = subperm(a,b,epat="/"+str(max_time(a,b)),max_cores=max_cores)
	nres = filterdown(res,a,b)
	res=nres
	print("Minified to "+str(len(res))+" permutation(s)")
	if(len(res) >= 5):
		print("First 5 combinations:")
		for i in range(-1,-6,-1):
			print(str(abs(i))+".")
			print(pretty_print(res[i-1]))
	else:
		print("First "+str(len(res))+" combinations:")
		for i in range(len(res)):
			print(str(abs(i))+".")
			print(pretty_print(res[i-1]))
	tot=0
	c=0
	for r in res:
		t1 = reduce(lambda x,y: x*y, [odds[x] for x in r[0]])
		t2 = reduce(lambda x,y: x*y, [odds[x] for x in r[1]])
		tot+=t1*t2*math.factorial(len(r[0]))
		c+=1
	m=100
	if(a==b):
		m*=14/392
	resrs = 0
	if(tot != 0):
		resrs = c/tot
		mult_factor = 1
		if(abs(a-b) > 5 and a+b < 165): # high difference, low scoring game =  add big factor
			mult_factor += 9
		if(a+b > 38): # scored more than 37 total is higher than the median game, add exponential factor with how much bigger
			mult_factor += 1 << (((a+b)-37)//10)
	resrs=str(math.floor(resrs))
	all_permuts_have_6_1=False
	if(resrs == "0"):
		resrs="\u221E?"
		all_permuts_have_6_1=True
	total_taken="took "+str(total)+" of highest bound "+str(max_time(a,b))
	if(total == 1):
		total_taken="already precached in path file"
	fff=resrs+" \"rarity score\" from "+str(c)+" games, "+total_taken
	fff+="\nMax permutations to score: "+str(len(res))
	fff+="\nNote: rarity score is a terrible metric, it's usually better to judge via max permutations to A-B score or if all the permutations have a 6-1 score"
	if(all_permuts_have_6_1):
		fff+="\nNote: \u221E rarity score is usually caused with insanely high final scores or all permutations requiring a 6-1 scoring event (e.g. final scores of 6-1, 10-1, 999-1)"
	total=0
	if(results_fn not in ["", None, "n", "false"]):
		real_name=results_fn.replace("{a}", str(a)).replace("{b}", str(b))
		with open(real_name, "w+") as f:
			arr=[pretty_print(tally) for tally in res]
			text="GOAL SCORE: "+str(a)+"-"+str(b)+"\n"+str(len(res))+" permutations\n---\n"+"\n".join([str(i+1)+". \n"+e for i,e in enumerate(arr)])
			f.write(text)
	if(cache_results in ["y","Y",True,"yes"]):
		add_to_prestored(a,b,res,fn=fn)

	return fff
if __name__ == "__main__":
	parsed = parser.parse_args()
	get_prestored()
	try:
		print(perm(int(parsed.a),int(parsed.b),max_cores=int(parsed.cores), results_fn=parsed.output, cache_results=parsed.cache))
	except Exception as e:
		print(e)
