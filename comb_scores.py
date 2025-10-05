import math,os,json
from multiprocessing import Pool, cpu_count
from functools import reduce
from decimal import Decimal as D
from decimal import getcontext
max_cores = 5
getcontext().prec = 100
score_ways_one_dir = [(2,0),(3,0),(6,0),(6,1),(7,0),(8,0)]
score_ways = [e for e in score_ways_one_dir]
score_ways.extend([e[::-1] for e in score_ways_one_dir])
min_score_paths_one_dir = {}
min_score_paths = {}
with open("prestored_paths.json", "r+") as f:
	loaded=json.load(f)
	for e in list(loaded.keys()):
		min_score_paths[e] = tuple(loaded[e])
dead_ends = [(0,1),(1,0),(1,1),(2,1),(1,2),(3,1),(1,3),(4,1),(1,4),(5,1),(1,5)]
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
def recursion(a,b,paths,ap,bp,lvl,epat,final,resultant):
	ap,bp,pprev,fls,finl=_perm(a, b, paths, ap, bp, lvl=lvl, epat=epat)
	final = finl
	resultant = []
	if(fls[1]==0):
		final.append((ap,bp))
	if(fls[0]==0):
		resultant.append((ap,bp))
	return final,resultant
def max_time(a,b):
	return len(score_ways)**(a//2+b//2)
def _perm(a,b,paths=[],a_path=[],b_path=[],flags=[0],lvl=0,epat=""):
	global total
	final=[]
	total+=1
	if(total % 255 == 0):
		print(total, end="/"+epat+"\r")
	if(a<0 or b<0 or (a,b) in dead_ends):
		return [0],[0],paths,[1,1],final
	for p in list(min_score_paths.keys()): # get endings if we're low enough
		if(p == str(a)+"-"+str(b)):
			for path_sub in min_score_paths[p]:
				a_path_clone=a_path.copy()
				b_path_clone=b_path.copy()
				a_path_clone.extend(path_sub[0])
				b_path_clone.extend(path_sub[1])
				final.append((a_path_clone,b_path_clone))
			return a_path,b_path,paths,[0,0],final
	resultant=[]
	recursion_fs=[]
	arglist=[]
	if(lvl == 0):
		pool = Pool(processes=max_cores)
		for p in score_ways: # get rest of paths
			arglist.append((a-p[0],b-p[1],paths,a_path+[p[0]],b_path+[p[1]],lvl+1,epat,final,resultant))
		res_tuple = pool.starmap(recursion,arglist)
		for finall,resultantt in res_tuple:
			final.extend(finall)
			resultant.extend(resultantt)
	else:
		for p in score_ways:
			finall,resultantt=recursion(a-p[0],b-p[1],paths,a_path+[p[0]],b_path+[p[1]],lvl+1,epat,final,resultant)
			final.extend(finall)
			resultant.extend(resultantt)
	for r in resultant:
		if(sum(r[0]) == a and sum(r[1]) == b):
			paths.append((a_path+[p[0]], b_path+[p[1]]))
	if(lvl > 0):
		return a_path, b_path, paths, [0,1], final
	print("Found "+str(len(final))+" base permutations                               ")
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
	for v in res:
		condition = True
		try:
			condition = len(v)!=2 or len(v[0])==0 or len(v[1])==0 or sum(v[0]) != av or sum(v[1]) != bv
		except Exception as e:
			print(e)
			pass
		if(condition):
			continue
		v[0].sort()
		v[1].sort()
		a,b = tuple(v[0]), tuple(v[1])
		if((a not in seen_a and b not in seen_b) and (a not in seen_b and b not in seen_a)):
			seen_a.add(a)
			seen_b.add(b)
			newres.append((v[0],v[1]))
	return newres
def perm(a,b):
	global total
	s1 = []
	s3 = []
	_,_,_,_,res = _perm(a,b,epat=str(max_time(a,b)))
	seen_a = []
	seen_b = []
	res = filterdown(res,a,b)
	print("Minified to "+str(len(res))+" permutation(s), including rearrangements of scores")
	print("(Up to) First 5 combinations:")
	print(res[:5])
	tot=0
	c=0
	for r in res:
		t1 = reduce(lambda x,y: x*y, [odds[x] for x in r[0]])
		t2 = reduce(lambda x,y: x*y, [odds[x] for x in r[1]])
		tot+=t1*t2
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
	if(resrs == "0"):
		resrs="\u221E?"
	total_taken="took "+str(total)+" of highest bound "+str(max_time(a,b))
	if(total == 1):
		total_taken="already precached in json file"
	fff=resrs+" \"rarity score\" from "+str(c)+" games, "+total_taken
	fff+="\nMax permutations to score: "+str(len(res))
	fff+="\nNote that rarity score is a terrible metric, it's usually better to judge via max permutations to A-B score"
	total=0
	return fff
tas=int(input("Team A score: "))
tbs=int(input("Team B score: "))
print(perm(tas,tbs))
