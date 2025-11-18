import pickle,math,sys,argparse,shutil
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
import threading
import time
from matplotlib.animation import FuncAnimation
from scoricomb import *

parser = argparse.ArgumentParser(
	prog="scoricomb-presave",
	description="Pre-stores score permutations for faster calculations when finding higher score permutations")
parser.add_argument("max_score")
parser.add_argument("-o", "--output", action="store_const", const="prestored_paths.pkl", default="prestored_paths.pkl")
parser.add_argument("-s", "--from-scratch", action="store_true",default=False)

fig,ax = plt.subplots()
perm_count_table = np.zeros([50,50])
def update_plots(frame=20,drawcanv=False):
	global perm_count_table
#	for (i,j), _ in np.ndenumerate(perm_count_table):
#		if i>j:
#			perm_count_table[i,j]=0
#	print(perm_count_table)
	mat.set_data(perm_count_table)
	mat.set_clim(vmin=0, vmax=np.max(perm_count_table))
	if(drawcanv):
		fig.canvas.draw()
	return [plt]

def update_grid_data():
	global perm_count_table
	dict={}
	with open("prestored_paths.pkl", "rb") as f:
		dict=pickle.load(f)
	for (i,j), value in np.ndenumerate(perm_count_table):
		key=str(i)+"-"+str(j)
		if i>j:
			perm_count_table[i,j]=0
			continue
		if key in dict and i<=j:
			if len(dict[key]) == 0:
				perm_count_table[i,j] = 0
				continue
			perm_count_table[i,j] = math.log2(len(dict[key]))
	return perm_count_table

mat = plt.imshow(np.zeros([50,50]),cmap="plasma")
try:
	mat = plt.imshow(update_grid_data(), cmap="plasma")
except Exception as e:
	print(e)
fig.colorbar(mat)

score_ways_one_dir = [(2,0),(3,0),(6,0),(6,1),(7,0),(8,0)]
score_ways = [e for e in score_ways_one_dir]
score_ways.extend([e[::-1] for e in score_ways_one_dir])
perm_count_table = np.zeros([50,50])
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
	global perm_count_table
	dict = {}
	with open(fn, "rb+") as f:
		dict = pickle.load(f)
	k=0
	for b in range(max_sqrt):
		try:
			for a in range(b,max_sqrt):
				if(str(a)+"-"+str(b) in dict):
					if(len(dict[str(a)+"-"+str(b)]) == 0 or a>b):
						update_plots()
						continue
					perm_count_table[a, b] = math.log2(len(dict[str(a)+"-"+str(b)]))
					update_plots()
					continue
				_,_,_,_,res=subperm(a,b,epat=", processing "+str(a)+"-"+str(b)+", "+str(b*max_sqrt+a)+"/"+str(max_sqrt**2))
				res=filterdown(res,a,b)
				dict[str(a)+"-"+str(b)] = [list(r) for r in res]
				dict[str(b)+"-"+str(a)] = [reversed(list(r)) for r in res]
				if(len(res) == 0 or a>b):
					continue
				perm_count_table[a, b] = math.log2(len(res))
				update_plots()
				with open(fn,"wb+") as f:
					pickle.dump(dict,f)
		except KeyboardInterrupt:
			dict["6-0"].extend([([3,3],[0,0]),([2,2,2],[0,0,0])])
			dict["7-0"].extend([([3,2,2],[0,0,0])])
			dict["8-0"].extend([([3,3,2],[0,0,0]),([2,2,2,2],[0,0,0,0]),([6,2],[0,0])])
			with open(fn, "wb+") as f:
				pickle.dump(dict, f)
			return 1
	dict["6-0"]=[([6],[0]),([3,3],[0,0]),([2,2,2],[0,0,0])]
	dict["7-0"]=[([7],[0]),([3,2,2],[0,0,0])]
	dict["8-0"]=[([8],[0]),([3,3,2],[0,0,0]),([2,2,2,2],[0,0,0,0]),([6,2],[0,0])]
	update_plots()
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
print(parsed.from_scratch)
if parsed.from_scratch:
	presave(fn=parsed.output,max_vals=12)
	print("done")
fig.gca().set_aspect('equal', adjustable='box')
def proc_matplot():
	global fig, plt
	try:
		print("Started plot")
#		ani=FuncAnimation(fig,update_plots,frames=200,interval=2000)
		update_grid_data()
		plt.show()
	except Exception as e:
		print(e)
def proc_calc():
	for i in range(0,int(parsed.max_score)+1):
		get_prestored(fn=parsed.output)
		if(presavev2(parsed.output,int(parsed.max_score))==1):
			break
		update_plots()
def proc_refresh():
	pass
#	while 1:
#		time.sleep(1)
#		update_grid_data()
#		update_plots(drawcanv=True)
i_proc_matplot=multiprocessing.Process(target=proc_refresh)
i_proc_calc=multiprocessing.Process(target=proc_calc)
if __name__=="__main__":
	i_proc_calc.start()
	i_proc_matplot.start()
	proc_matplot()
