"""
USE: python <PROGNAME> (options) 
OPTIONS:
    -h : print this help message and exit
    -d FILE : use FILE as data to create a new lexicon file
    -l FILE : create OR read lexicon file FILE
    -t FILE : apply lexicon to test data in FILE
"""
################################################################

import sys, re, getopt

################################################################
# Command line options handling, and help

opts, args = getopt.getopt(sys.argv[1:],'hd:l:t:')
opts = dict(opts)

def printHelp():
    help = __doc__.replace('<PROGNAME>',sys.argv[0],1)
    print('-' * 60, help, '-' * 60, file=sys.stderr)
    sys.exit()
    
if '-h' in opts:
    printHelp()

if len(args) > 0:
    print("\n** ERROR: no arg files - only options! **", file=sys.stderr)
    printHelp()

if '-l' not in opts:
    print("\n** ERROR: must specify lexicon file name (opt: -l) **", file=sys.stderr)
    printHelp()

################################################################

# Function to split up a line of "Brill format" data into a list
# of word/tag pairs. 

def parseLine(line):
    wdtags = line.split()
    for i in range(len(wdtags)):
        (wd,xc,tag) = wdtags[i].rpartition('/')
        wdtags[i] = (wd,tag)
    return wdtags

####################

wordTagCounts = {}
    # This is main data structure of lexicon - a two-level
    # dictionary, mapping words->tags->counts. 

if '-d' in opts:
    
    print('<reading data for new lexicon ....>', file=sys.stderr)
    data = open(opts['-d'],'r')
    for line in data:
        for wd,tag in parseLine(line):
            if wd not in wordTagCounts:
                wordTagCounts[wd] = {}
            if tag in wordTagCounts[wd]:
                wordTagCounts[wd][tag] += 1
            else:
                wordTagCounts[wd][tag] = 1

    print('<writing lexicon to file....>', file=sys.stderr)
    lex = open(opts['-l'],'w')
    for wd in wordTagCounts:
        print(wd, end=' ', file=lex)
        tags = sorted(wordTagCounts[wd], key=lambda x:wordTagCounts[wd][x], reverse=True)
        for tag in tags:
            print('%s:%d' % (tag,wordTagCounts[wd][tag]), end=' ', file=lex)
        print(file=lex)
    lex.close()    
    
else:
    
    print('<reading lexicon file ....>', file=sys.stderr)
    lex = open(opts['-l'],'r')
    for line in lex:
        parts = line.split()
        wd = parts[0]
        if wd not in wordTagCounts:
           wordTagCounts[wd] = {}     
        for tc in parts[1:]:
            (tag,x,c) = tc.rpartition(':')
            wordTagCounts[wd][tag] = int(c)
    lex.close()

print('<done>', file=sys.stderr)

################################################
# ANALYSE LEXICON, to compute:
# -- proportion of types that have more than one tag
# -- accuracy naive tagger would have on the training data
# -- most common tags globally

tagCounts = {}
ambiguousWords = 0 
allWords = len(wordTagCounts)
correctTokens = 0
allTokens = 0

for wd in wordTagCounts:
    values = wordTagCounts[wd].values()
    if len(values) > 1:
        ambiguousWords += 1
    correctTokens += max(values)
    allTokens += sum(values)
    for t,c in wordTagCounts[wd].items():
        if t in tagCounts:
            tagCounts[t] += c
        else:
            tagCounts[t] = c

print('Proportion of word types that are ambiguous: %5.1f%% (%d / %d)' % \
        ((100.0*ambiguousWords)/allWords,ambiguousWords,allWords), file=sys.stderr)

print('Accuracy of naive tagger on training data: %5.1f%% (%d / %d)' % \
        ((100.0*correctTokens)/allTokens,correctTokens,allTokens), file=sys.stderr)

tags = sorted(tagCounts, key=lambda x:tagCounts[x], reverse=True)

print('Top Ten Tags by count:', file=sys.stderr)
for tag in tags[:10]:
    count = tagCounts[tag]
    print('   %9s %6.2f%% (%5d / %d)' % \
          (tag,(100.0*count)/allTokens,count,allTokens), file=sys.stderr)

################################################
# Function to 'guess' tag for unknown words

digitRE = re.compile('\d')
jj_ends_RE = re.compile('(ed|us|ic|ble|ive|ary|ful|ical|less)$')
        
def tagUnknown(wd):
    #return 'UNK'
    #return 'NN'
    #return 'NNP'
    if wd[0:1].isupper():
        return 'NNP'
    if '-' in wd:
        return 'JJ'
    if digitRE.search(wd):
        return 'CD'
    if jj_ends_RE.search(wd):
        return 'JJ'
    if wd.endswith('s'):
        return 'NNS'
    if wd.endswith('ly'):
        return 'RB'
    if wd.endswith('ing'):
        return 'VBG'

################################################
# Apply naive tagging method to test data, and score performance

if '-t' in opts:
    
    print('<tagging test data ....>', file=sys.stderr)
    
    # Compute 'most common' tag for each known word - store in maxtag dictionary
    maxtag = {}
    for wd in wordTagCounts:
        tags = sorted(wordTagCounts[wd], key=lambda x:wordTagCounts[wd][x], reverse=True)
        maxtag[wd] = tags[0]

    # Tag each word of test data, and score
    test = open(opts['-t'],'r')
    alltest = 0
    correct = 0
    for line in test:
        for wd,truetag in parseLine(line):
            if wd in maxtag:
                newtag = maxtag[wd]
            else:
                newtag = tagUnknown(wd)
            alltest += 1
            if newtag == truetag:
                correct += 1
            
    print("Score on test data: %5.1f%% (%5d / %5d)" % \
          ((100.0*correct)/alltest,correct,alltest), file=sys.stderr)
    
    print('<done>', file=sys.stderr)

################################################

