import matplotlib.pyplot as plt
import matplotlib, traceback
from matplotlib.animation import FuncAnimation
import numpy as np
import pickle, math, scoriserial

size = 40
grid_dat=np.zeros([size,size])
impossible_scores=[(0,1),(1,1),(1,2),(1,3),(1,4),(1,5),(1,7)]
Xcp = 0
Ycp = 0
max_len = 0
def increment_xcp_ycp():
	global Xcp, Ycp, size
	Xcp += 1
	if(Xcp >= size):
		Xcp = 0
		Ycp += 1
	if(Ycp >= size):
		Ycp = 0
def update_lims():
	try:
		global mat, grid_dat
		min_v, max_v = (-1, 1)
		try:
			min_v, max_v = (grid_dat.min(), grid_dat.max())
		except:
			print("AAAA" + e)
		mat.set_clim(min_v, max_v)
	except Exception as e:
		e.print_stack()
def update_grid_data(frame=0):
#	global grid_dat, im
	try:
		i,j = (Xcp, Ycp)
		value = scoriserial.get_score("prestored_paths.scoricomb", j,i)
		if(j<i):
			grid_dat[i, j] = -1
			increment_xcp_ycp()
			return grid_dat
		if(len(value) == 1 and value[0] == -1):
			grid_dat[i,j]=-1
			increment_xcp_ycp()
			return grid_dat
		if(len(value) == 0):
			grid_dat[i, j] = 0
			increment_xcp_ycp()
			return grid_dat
		grid_dat[i, j] = len(value)
		for impossible_score in impossible_scores:
			grid_dat[impossible_score]=-1
		increment_xcp_ycp()
		return grid_dat
	except Exception as e:
		print(e)
		increment_xcp_ycp()
		return grid_dat
fig,ax = plt.subplots()
mat = ax.matshow(update_grid_data(), cmap="plasma", norm="symlog")
cb = plt.colorbar(mat)

def update(data):
	mat.set_data(data)
	update_lims()
def data_gen():
	while True:
		try:
			yield update_grid_data()
		except:
			pass
ani=FuncAnimation(fig, update, data_gen, interval=0)
#fig=plt.figure()
#im=plt.imshow(grid_dat, cmap="plasma", origin='upper') # 'binary' colormap for black/white, 'upper' origin for typical array indexing
#plt.grid(which='major', color='gray', linestyle='-', linewidth=1)
#plt.xticks(np.arange(-0.5, grid_dat.shape[1], 1), [])
#plt.yticks(np.arange(-0.5, grid_dat.shape[0], 1), [])

# Ensure square aspect ratio
plt.gca().set_aspect('equal', adjustable='box')

#anim=FuncAnimation(fig,update_grid_data,frames=1000,interval=2000,init_func=update_grid_data)
plt.show()
