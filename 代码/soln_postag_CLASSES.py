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

class CommandLine:
    def __init__(self):
        opts, args = getopt.getopt(sys.argv[1:],'hd:l:t:')
        opts = dict(opts)
        self.dataFile = None
        self.testFile = None

        if '-h' in opts:
            self.printHelp()

        if len(args) > 0:
            print("\n** ERROR: no arg files - only options! **", file=sys.stderr)
            self.printHelp()

        if '-l' in opts :
            self.lexFile = opts ['-l']
        else:
            print("\n** ERROR: must specify lexicon file name (opt: -l) **", file=sys.stderr)
            self.printHelp()

        if '-d' in opts :
            self.dataFile = opts ['-d']
        
        if '-t' in opts :
            self.testFile = opts ['-t']

    def printHelp(self):
            help = __doc__.replace('<PROGNAME>',sys.argv[0],1)
            print('-' * 60, help, '-' * 60, file=sys.stderr)
            exit()

################################################################

class ParsePosData:
    def __init__(self,file):
        self.file = file

    def lines(self):
        f = open(self.file,'r')
        for line in f:
            yield self.parseLine(line)
            # Use of "yield" here makes this a 'generator function'
            # -- a tidy python way of constructing an iterator
        f.close()

    def parseLine(self,line):
        wdtags = line.split()
        for i in range(len(wdtags)):
            (wd,xc,tag) = wdtags[i].rpartition('/')
            wdtags[i] = (wd,tag)
        return wdtags

################################################################

class Lexicon:
    def __init__(self):
        self.wordTagCounts = {}
        self.tagCounts = {}
        
    def addWordTagCount(self,wd,tag,v):
        if wd not in self.wordTagCounts:
            self.wordTagCounts[wd] = {}
        if tag in self.wordTagCounts[wd]:
            self.wordTagCounts[wd][tag] += v
        else:
            self.wordTagCounts[wd][tag] = v
    
    def addTagCount(self,tag,v):
        if tag in self.tagCounts:
            self.tagCounts[tag] += v
        else:
            self.tagCounts[tag] = v
    
    def readData(self,dataFile):
        data = ParsePosData(dataFile)
        for line in data.lines():
            for (wd,tag) in line:
                self.addWordTagCount(wd,tag,1)

    def writeLexicon(self,lexfile):
        lex = open(lexfile,'w')
        for wd in self.wordTagCounts:
            print(wd, file=lex, end=' ')

            tags = sorted(self.wordTagCounts[wd], key=lambda x:self.wordTagCounts[wd][x], reverse=True)

            for tag in tags:
                print('%s:%d' % (tag,self.wordTagCounts[wd][tag]), end=' ', file=lex)
            print(file=lex)
        lex.close()
        
    def readLexicon(self,lexfile):
        self.wordTagCounts = {}
        lex = open(lexfile,'r')
        for line in lex:
            parts = line.split()
            wd = parts[0]
            for tc in parts[1:]:
                (tag,x,c) = tc.rpartition(':')
                self.addWordTagCount(wd,tag,int(c))
        lex.close()
        
    def words(self):
        return self.wordTagCounts.keys()

    def getMaxTag(self,wd):
        if wd in self.wordTagCounts:
            tags = sorted(self.wordTagCounts[wd], key=lambda x:self.wordTagCounts[wd][x], reverse=True)
            return tags[0]
        else:
            return None

    def analyseLexicon(self):
        ambiguousWords = 0
        allWords = len(self.wordTagCounts)
        correctTokens = 0
        allTokens = 0
        for wd in self.wordTagCounts:
            values = self.wordTagCounts[wd].values()
            if len(values) > 1:
                ambiguousWords += 1
            correctTokens += max(values)
            allTokens += sum(values)
            for t,c in self.wordTagCounts[wd].items():
                self.addTagCount(t,c)
        
        print('Proportion of word types that are ambiguous: %5.1f%% (%d / %d)' % \
                ((100.0*ambiguousWords)/allWords,ambiguousWords,allWords), file=sys.stderr)
        print('Accuracy of naive tagger on training data: %5.1f%% (%d / %d)' % \
                ((100.0*correctTokens)/allTokens,correctTokens,allTokens), file=sys.stderr)
        
        tags = sorted(self.tagCounts, key=lambda t:self.tagCounts[t], reverse=True)
        
        print('Top Ten Tags by count:', file=sys.stderr)
        for tag in tags[:10]:
            count = self.tagCounts[tag]
            print('   %9s %6.2f%% (%5d / %d)' % \
                  (tag,(100.0*count)/allTokens,count,allTokens), file=sys.stderr)

################################################################

class NaiveTagger:
    def __init__(self,lexicon):
        self.maxtag = {}
        self.digitRE = re.compile('\d')
        self.jj_ends_RE = re.compile('(ed|us|ic|ble|ive|ary|ful|ical|less)$')
        
        for wd in lexicon.words():
            self.maxtag[wd] = lexicon.getMaxTag(wd)
            
    def tagfile(self,file):
        test = ParsePosData(file)
        alltest = 0
        correct = 0
        for line in test.lines():
            for (wd,truetag) in line:
                alltest += 1
                if truetag == self.tagword(wd):
                    correct += 1
        print("Score on test data: %5.1f%% (%5d / %5d)" % \
            ((100.0*correct)/alltest,correct,alltest), file=sys.stderr)
        
    def tagword(self,wd):
        if wd in self.maxtag:
            return self.maxtag[wd]
        else:
            return self.tagUnknown(wd)

    def tagUnknown(self,wd):
#         return 'UNK'
#         return 'NN'
#         return 'NNP'
        if wd[0:1].isupper():
            return 'NNP'
        if '-' in wd:
            return 'JJ'
        if self.digitRE.search(wd):
            return 'CD'
        if self.jj_ends_RE.search(wd):
            return 'JJ'
        if wd.endswith('s'):
            return 'NNS'
        if wd.endswith('ly'):
            return 'RB'
        if wd.endswith('ing'):
            return 'VBG'
        return 'NN'

################################################################

if __name__ == '__main__':
    config = CommandLine()
    lexicon = Lexicon()
    
    if config.dataFile:
        print('<reading data for new lexicon ....>', file=sys.stderr)
        lexicon.readData(config.dataFile)
        print('<writing lexicon to file....>', file=sys.stderr)
        lexicon.writeLexicon(config.lexFile)
    else:
        print('<reading lexicon file ....>', file=sys.stderr)
        lexicon.readLexicon(config.lexFile)
    
    print('<analysing lexicon ....>', file=sys.stderr)
    lexicon.analyseLexicon()
    
    if config.testFile:
        print('<tagging test data ....>', file=sys.stderr)
        naive = NaiveTagger(lexicon)
        naive.tagfile(config.testFile)

    print('<done>', file=sys.stderr)


