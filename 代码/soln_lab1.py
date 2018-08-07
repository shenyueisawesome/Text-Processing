
# Lab 1 solution
# 
# There's lots of ways to complete this simple exercise.
# 
# Need to read in the lines and store them (e.g. in a 
# list), so can print them in reverse. 
# 
# Can either number the lines as you read them in, or 
# after, or can infer the line nums as printing. 
# 
# To print in reverse order, can either explicitly 
# reverse the list (by calling its ".reverse()" method),
# or use a down-counting for-loop, or a while loop
# that ".pop()"s the final element. 
# 
# Here's just one version ...

import sys

lines = []
linenum = 0

with open(sys.argv[1],'r') as infs:
    for line in infs:
        linenum += 1
        lines.append((linenum,line))

lines.reverse()

for (linenum,line) in lines:
    print(linenum, ':', line, end='')

