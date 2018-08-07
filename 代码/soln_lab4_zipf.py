"""
USE: python <PROGNAME> (options) datafile1 ... datafileN
OPTIONS:
    -h : print this help message and exit
    -s FILE : read stoplist words from FILE
"""
################################################################

import sys, re, getopt
import pylab as p

opts, args = getopt.getopt(sys.argv[1:],'hs:')
opts = dict(opts)

if '-h' in opts:
    help = __doc__.replace('<PROGNAME>',sys.argv[0],1)
    print('-' * 60, help, '-' * 60, file=sys.stderr)
    sys.exit()

################################################################
# Load stop list (optional)

stops = set()
if '-s' in opts:
    with open(opts['-s']) as stopf:
        for line in stopf:
            stops.add(line.strip())

################################################################
# Count words in data file(s)

word = re.compile('\w+')
wdcounts = {}

for file in args:
    with open(file) as inf:
        for line in inf:
            for wd in word.findall(line.lower()):
                if wd in stops: continue
                if wd not in wdcounts:
                    wdcounts[wd] = 0
                wdcounts[wd] += 1

################################################################
# Sort words / print top N

topN = 20
words = sorted(wdcounts,reverse=True,key=lambda v:wdcounts[v])
counts = sorted(wdcounts.values(),reverse=True)

print('TYPES: ', len(words), file=sys.stderr)
print('TOKENS:', sum(counts), file=sys.stderr)

for wd in words[:topN]:
    print(wd, ':', wdcounts[wd], file=sys.stderr)

################################################################
# Plot freq vs. rank

ranks = range(1,len(counts)+1)

p.figure()
p.plot(ranks,counts)
p.title('freq vs rank')

################################################################
# Plot cumulative freq vs. rank

cumulative = list(counts) # makes (shallow) copy of counts list

for i in range(1,len(counts)):
    cumulative[i] += cumulative[i-1]

p.figure()
p.plot(ranks,cumulative)
p.title('cumulative freq vs rank')

################################################################
# Plot log-freq vs. log-rank

logfreq = [p.log(c) for c in counts]
logrank = [p.log(r) for r in ranks]

p.figure()
p.plot(logrank,logfreq)
p.title('log-freq vs log-rank')

################################################################
# Display figures

p.show()

################################################################
