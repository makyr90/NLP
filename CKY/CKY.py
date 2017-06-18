import json
import numpy as np
from anytree import Node,RenderTree
import queue


def CKY_parser(grammar,sentence):
	

	wordList = sentence.split()

	cky_table = np.empty([len(wordList)+1,len(wordList)],dtype='U10000')

	trace={}
	for idx in range(len(wordList)):
		cky_table[-1,idx] = wordList[idx]

	for idx in range(len(wordList)):
		cky_table[-2,idx] = grammar[cky_table[-1,idx]]
		trace[(cky_table.shape[0]-2,idx)] = [(cky_table.shape[0]-1,idx)]


	width = 0
	for idx in range((cky_table.shape[0]-3),-1,-1):
		width+=1
		for jdx in range(cky_table.shape[1] - width):
			diagonal = (cky_table.shape[0]-2,jdx+width)

			for idx2 in range(idx,cky_table.shape[0]-2):
				rule = (cky_table[idx2+1,jdx],cky_table[diagonal[0],diagonal[1]])
				try:
					val = grammar[rule]
					cky_table[idx,jdx] = val
					trace[(idx,jdx)] = [(idx2+1,jdx),(diagonal[0],diagonal[1])]
				except KeyError:
					diagonal = (diagonal[0]-1,diagonal[1]-1)
					continue

			
				diagonal = (diagonal[0]-1,diagonal[1]-1)

	
	print("CKY table:")
		
	for idx in range(cky_table.shape[0]-1):
		for jdx in range(cky_table.shape[1]):
			if (jdx<idx):
				print(cky_table[idx,jdx], end=" - ")
			elif (jdx==idx):
				print(cky_table[idx,jdx])
		print('\n')
	for word in wordList[:-1]:
		print(word,end=" - ")
	print(wordList[-1])
	print('\n') 

	return (cky_table,trace)

def extract_tree(cky_table,trace,grammar):

	parent_node = {}
	Q = queue.Queue()
	Q.put((0,0))
	q_val = Q.get()
	exec(str(cky_table[q_val[0],q_val[0]])+str((q_val[0]))+'= Node("'+cky_table[q_val[0],q_val[1]]+'")')
	clildren = []
	for child in trace[q_val]:
		parent_node[child] = q_val
		Q.put(child)
	while not Q.empty():
		q_val = Q.get()
		parent_tuple = parent_node[q_val]
		exec(str(cky_table[q_val[0],q_val[1]])+str(q_val[0])+'= Node("'+str(cky_table[q_val[0],q_val[1]])+'",parent = '+str(cky_table[parent_tuple[0],parent_tuple[1]])+str(parent_tuple[0])+')')
		try:
			for child in trace[q_val]:
				parent_node[child] = q_val
				Q.put(child)
		except KeyError:
			try:
				for child in trace[str(q_val)]:
					parent_node[child] = q_val
					Q.put(child)
			except KeyError:
				continue
	print("Parse Tree")
	
	#plot tree
	for pre, fill, node in RenderTree(eval(str(cky_table[0,0])+"0")):
		print("%s%s" % (pre, node.name))
	
def depedency_tree(cky_table,trace,grammar):
	
	heads_words =  np.empty([cky_table.shape[0],cky_table.shape[1]],dtype='U10000')
	heads_words[-1,:] = cky_table[-1,:]
	heads_words[-2,:] = cky_table[-1,:]
	width = 0
	for idx in range((heads_words.shape[0]-3),-1,-1):
		width+=1
		for jdx in range(heads_words.shape[1] -width):
			if (not(cky_table[idx,jdx]=="")):
				specifier1 = cky_table[idx,jdx]
				val = trace[(idx,jdx)]
				if(len(val)>1):
					for cell in val:
						
						specifier2 = cky_table[cell[0],cell[1]]
						
						if (specifier1 == specifier2):
							heads_words[idx,jdx] = heads_words[cell[0],cell[1]]
							break
						
						try:

							rule = grammar[str(specifier2)]

							if (rule == specifier1):
								heads_words[idx,jdx] = heads_words[cell[0],cell[1]]
						except KeyError:
							continue
	
	depedency_tree ={}
	for word in heads_words[-1]:
		depedency_tree[word] =[]

	Q = queue.Queue()
	Q.put((0,0))
	q_val = Q.get()
	parent = heads_words[q_val[0],q_val[1]]
	for child in trace[q_val]:
		Q.put(child)
		childval = heads_words[child[0],child[1]]
		if (parent != childval):
			depedency_tree[parent].append(childval)
	while not Q.empty():
		q_val = Q.get()
		parent = heads_words[q_val[0],q_val[1]]
		try:
			for child in trace[q_val]:
				Q.put(child)
				childval = heads_words[child[0],child[1]]
				if (parent != childval):
					depedency_tree[parent].append(childval)
		except KeyError:
				continue
	
	for k,v in depedency_tree.items():
		exec(k+'= Node("'+k+'")')
	for k,v in depedency_tree.items():
		for val in v:
			exec(val+'.parent ='+k)

	print("Depedency Tree")
	# plot tree
	for pre, fill, node in RenderTree(eval(str(heads_words[0,0]))):
		print("%s%s" % (pre, node.name))

	
#load grammars
grammar1 = json.load(open("grammar1.txt"))
for k,v in grammar1.items():
	if ("(" in k):
		grammar1[eval(k)] = grammar1.pop(k)

grammar2 = json.load(open("grammar2.txt"))
for k,v in grammar2.items():
	if ("(" in k):
		grammar2[eval(k)] = grammar2.pop(k)

table,trace = CKY_parser(grammar2,"egw protimw mia proinh pthsh pros thn Athina")
if (table[0,0] == "S"):
	extract_tree(table,trace,grammar2)
	depedency_tree(table,trace,grammar2)

# table,trace = CKY_parser(grammar1,"I saw the man with the telescope from the hill")
# if (table[0,0] == "S"):
# 	extract_tree(table,trace,grammar1)