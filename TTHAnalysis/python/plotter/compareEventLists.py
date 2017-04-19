#! /usr/bin/env python
def getEventLists(file1, file2):
	## Build event lists:
	list1 = []
	list2 = []
	with open(file1, 'r') as file:
		for line in file:
			try:
				run,lumi,ev = tuple(map(int, line.split(',')))
				list1.append((run,lumi,ev))
			except ValueError:
				continue
	with open(file2, 'r') as file:
		for line in file:
			try:
				run,lumi,ev = tuple(map(int, line.split(',')))
				list2.append((run,lumi,ev))
			except ValueError:
				continue

	return list1, list2

def compareEventLists(file1, file2):
	list1, list2 = getEventLists(file1, file2)

	assert(len(list1) == len(set(list1)))
	assert(len(list2) == len(set(list2)))

	list1 = set(list1)
	list2 = set(list2)
	agree_on = list1.intersection(list2)
	excess1 = list1.difference(list2)
	excess2 = list2.difference(list1)

	print 80*'-'
	maxlen = max(len(str(len(list1))), len(str(len(list2))) )
	outfor = ("total: {0:%dd}, unique: {1:%dd} , common: {2:%dd} ({3:.1%%})"
		                   % (maxlen,maxlen,maxlen))
	print ("%50s %s" % (file1,
		   outfor.format(len(list1),
		   	             len(excess1),
		   	             len(agree_on),
		   	             float(len(agree_on))/len(list1))))
	print ("%50s %s" % (file2,
		   outfor.format(len(list2),
		   	             len(excess2),
		   	             len(agree_on),
		   	             float(len(agree_on))/len(list2))))
	# print (' (total distinct events: %d)' %
	# 	    (len(agree_on)+len(excess1)+len(excess2)))
	print 80*'-'

def makeVennDiagram(file1, file2):
	try:
		from matplotlib import pyplot as plt
		from matplotlib_venn import venn2, venn2_circles
	except ImportError:
		print "Missing matplotlib_venn module, skipping venn diagram."
		return

	list1, list2 = getEventLists(file1, file2)

	set1 = set(list1)
	set2 = set(list2)

	sizes = {
		'10': len(set1)-len(set1.intersection(set2)),
		'01': len(set2)-len(set1.intersection(set2)),
		'11': len(set1.intersection(set2)),
	}

	plt.figure(figsize=(7,7))
	v = venn2(subsets=sizes, set_labels=('tHq Selection', 'ttH Selection'))

	# Cosmetics
	v.get_patch_by_id('10').set_alpha(0.2)
	v.get_patch_by_id('10').set_color('red')
	if sizes['11'] > 0:
		v.get_patch_by_id('11').set_alpha(0.5)
		v.get_patch_by_id('11').set_color('red')

	c = venn2_circles(subsets=sizes, linestyle='solid', linewidth=1.0)
	c[1].set_lw(1.0)

	# Save the pdf
	from os import path as osp
	plotfilename = "%s_%s_venn.pdf" % (osp.splitext(osp.basename(file1))[0],
		                               osp.splitext(osp.basename(file2))[0])
	plt.savefig(plotfilename, format='pdf', bbox_inches='tight')
	print ' created venn diagram in %s' % plotfilename
	print 80*'-'

##---------------------------------------------------------------------------------
## User interface
if __name__ == "__main__":
	from optparse import OptionParser
	usage = """
	Compare two text files with event dumps for overlaps.
	%prog  list1.txt list2.txt
	"""

	parser = OptionParser(usage=usage)
	(options, args) = parser.parse_args()

	if len(args) > 1:
		compareEventLists(args[0], args[1])
		makeVennDiagram(args[0], args[1])
		exit(0)

	parser.print_help()
	exit(-1)



