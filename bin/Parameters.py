from __future__ import annotations
from bin.Log import Log
import getopt, glob, os, pickle, sys

class Parameters():
    """class to store arguments and debug utilities
    """
    # default values
    _ALLOWED_FORMATS = ('genbank', 'fasta')
    _DEF_OUTGROUP = list()
    _DEF_FRMT = _ALLOWED_FORMATS[0]
    _DEF_MIN_LEN = 16
    _DEF_MAX_LEN = 20
    _DEF_MIN_GC = 40.0
    _DEF_MAX_GC = 60.0
    _DEF_MIN_TM = 55.0
    _DEF_MAX_TM = 68.0
    _DEF_MIN_PCR = 120
    _DEF_MAX_PCR = 2400
    _DEF_MAX_TM_DIFF = 5.0
    _DEF_NUM_THREADS = 1
    _DEF_DEBUG = False
    _DEF_HELP = False
    
    def __init__(self, author:str, version:str) -> Parameters:
        # type hint attributes
        self.ingroupFns:list[str]
        self.outgroupFns:list[str]
        self.outFn:str
        self.format:str
        self.minLen:int
        self.maxLen:int
        self.minGc:float
        self.maxGc:float
        self.minTm:float
        self.maxTm:float
        self.minPcr:int
        self.maxPcr:int
        self.maxTmDiff:float
        self.disallowedLens:range
        self.numThreads:int
        self.debug:bool
        self.helpRequested:bool
        self.log:Log
        
        # parse the command line arguments (populates attributes)
        self.__parseArgs(author, version)
        
        # initialize a log if debugging
        if self.debug:
            self.log = Log()

    def __parseArgs(self, author:str, version:str) -> None:
        """parses command line arguments

        Args:
            author (str): the author of the program
            version (str): the version of the program

        Raises:
            ValueError: invalid/missing ingroup files
            ValueError: invalid/missing ingroup files
            ValueError: output file already exists
            ValueError: cannot write to output file
            ValueError: invalid/missing outgroup files
            ValueError: invalid/missing outgroup files
            ValueError: invalid disallowed sizes: not two value
            ValueError: invalid disallowed sizes: not int
            ValueError: invalid file format
            ValueError: invalid primer length: wrong num arguments
            ValueError: invalid primer length: not int
            ValueError: invalid GC: not two values
            ValueError: invalid GC: not numeric
            ValueError: invalid Tm: not two values
            ValueError: invalid Tm: not numeric
            ValueError: invalid PCR size: not two values
            ValueError: invalid PCR size: not int
            ValueError: Tm difference is not numeric
            ValueError: num threads not an integer
            ValueError: ingroup file argument is missing
            ValueError: output file argument is missing
        """
        # constants
        SEP = ","
        
        # flags
        INGROUP_FLAGS = ('-i', '--ingroup')
        OUT_FLAGS = ('-o', '--out')
        OUTGROUP_FLAGS = ('-u', '--outgroup')
        DISALLOW_FLAGS = ("-b", "--bad_sizes")
        FMT_FLAGS = ('-f', '--format')
        PRIMER_LEN_FLAGS = ('-p', '--primer_len')
        GC_FLAGS = ('-g', '--gc_range')
        TM_FLAGS = ('-t', '--tm_range')
        THREADS_FLAGS = ('-n', '--num_threads')
        PCR_LEN_FLAGS = ('-r', '--pcr_prod')
        TM_DIFF_FLAGS = ('-d', '--tm_diff')
        VERSION_FLAGS = ('-v', '--version')
        HELP_FLAGS = ('-h', '--help')
        DEBUG_FLAGS = ("--debug",)
        SHORT_OPTS = INGROUP_FLAGS[0][-1] + ":" + \
                    OUT_FLAGS[0][-1] + ":" + \
                    OUTGROUP_FLAGS[0][-1] + ":" + \
                    DISALLOW_FLAGS[0][-1] + ":" + \
                    FMT_FLAGS[0][-1] + ":" + \
                    PRIMER_LEN_FLAGS[0][-1] + ":" + \
                    GC_FLAGS[0][-1] + ":" + \
                    TM_FLAGS[0][-1] + ":" + \
                    PCR_LEN_FLAGS[0][-1] + ":" + \
                    TM_DIFF_FLAGS[0][-1] + ":" + \
                    THREADS_FLAGS[0][-1] + ":" + \
                    VERSION_FLAGS[0][-1] + \
                    HELP_FLAGS[0][-1]
        LONG_OPTS = (INGROUP_FLAGS[1][2:] + "=",
                    OUT_FLAGS[1][2:] + "=",
                    OUTGROUP_FLAGS[1][2:] + "=",
                    DISALLOW_FLAGS[1][2:] + "=",
                    FMT_FLAGS[1][2:] + "=",
                    PRIMER_LEN_FLAGS[1][2:] + "=",
                    GC_FLAGS[1][2:] + "=",
                    TM_FLAGS[1][2:] + "=",
                    PCR_LEN_FLAGS[1][2:] + "=",
                    TM_DIFF_FLAGS[1][2:] + "=",
                    THREADS_FLAGS[1][2:] + "=",
                    VERSION_FLAGS[1][2:],
                    HELP_FLAGS[1][2:],
                    DEBUG_FLAGS[0][2:])

        # messages
        IGNORE_MSG = 'ignoring unused argument: '
        ERR_MSG_1  = 'invalid or missing ingroup file(s)'
        ERR_MSG_2  = 'specified output file already exists'
        ERR_MSG_3  = 'cannot write to output file'
        ERR_MSG_4  = 'invalid or missing outgroup file(s)'
        ERR_MSG_5  = 'must specify exactly two integers for bad outgroup PCR product length'
        ERR_MSG_6  = 'bad outgroup PCR product lengths are not integers'
        ERR_MSG_7  = 'invalid format'
        ERR_MSG_8  = 'can only specify one primer length or a range (min,max)'
        ERR_MSG_9  = 'primer lengths are not integers'
        ERR_MSG_10 = 'must specify a range of GC values (min,max)'
        ERR_MSG_11 = 'gc values are not numeric'
        ERR_MSG_12 = 'must specify a range of Tm values (min, max)'
        ERR_MSG_13 = 'Tm values are not numeric'
        ERR_MSG_14 = 'can only specify one PCR product length or a range (min,max)'
        ERR_MSG_15 = 'PCR product lengths are not integers'
        ERR_MSG_16 = 'max Tm difference is not numeric'
        ERR_MSG_17 = 'num threads is not an integer'
        ERR_MSG_18 = 'must specify one or more ingroup files'
        ERR_MSG_19 = 'must specify an output file'

        def printHelp():
            GAP = " "*4
            EOL = "\n"
            SEP_1 = ", "
            SEP_2 = "|"
            SEP_3 = ","
            DEF_OPEN = ' (default: '
            CLOSE = ')'
            WIDTH = 21
            HELP_MSG = f"{EOL}Finds pairs of primers suitable for a group of input genomes{EOL}" + \
                       f"{GAP}{author}, 2024{EOL*2}" + \
                       f"usage:{EOL}" + \
                       f"{GAP}primerForge.py [-{SHORT_OPTS.replace(':','')}]{EOL*2}" + \
                       f"required arguments:{EOL}" + \
                       f'{GAP}{INGROUP_FLAGS[0] + SEP_1 + INGROUP_FLAGS[1]:<{WIDTH}}[file] ingroup filename or a file pattern inside double-quotes (eg."*.gbff"){EOL}' + \
                       f"{GAP}{OUT_FLAGS[0] + SEP_1 + OUT_FLAGS[1]:<{WIDTH}}[file] output filename{EOL*2}" + \
                       f"optional arguments: {EOL}" + \
                       f'{GAP}{OUTGROUP_FLAGS[0] + SEP_1 + OUTGROUP_FLAGS[1]:<{WIDTH}}[file(s)] outgroup filename or a file pattern inside double-quotes (eg."*.gbff"){EOL}' + \
                       f"{GAP}{DISALLOW_FLAGS[0] + SEP_1 + DISALLOW_FLAGS[1]:<{WIDTH}}[int,int] a range of PCR product lengths that the outgroup cannot produce{DEF_OPEN}same as '{PCR_LEN_FLAGS[1]}'{CLOSE}{EOL}" + \
                       f"{GAP}{FMT_FLAGS[0] + SEP_1 + FMT_FLAGS[1]:<{WIDTH}}[str] file format of the ingroup and outgroup {Parameters._ALLOWED_FORMATS[0]}{SEP_2}{Parameters._ALLOWED_FORMATS[1]}{DEF_OPEN}{Parameters._DEF_FRMT}{CLOSE}{EOL}" + \
                       f"{GAP}{PRIMER_LEN_FLAGS[0] + SEP_1 + PRIMER_LEN_FLAGS[1]:<{WIDTH}}[int(s)] a single primer length or a range specified as 'min,max'{DEF_OPEN}{Parameters._DEF_MIN_LEN}{SEP_3}{Parameters._DEF_MAX_LEN}{CLOSE}{EOL}" + \
                       f"{GAP}{GC_FLAGS[0] + SEP_1 + GC_FLAGS[1]:<{WIDTH}}[float,float] a min and max percent GC specified as a comma separated list{DEF_OPEN}{Parameters._DEF_MIN_GC}{SEP_3}{Parameters._DEF_MAX_GC}{CLOSE}{EOL}" + \
                       f"{GAP}{TM_FLAGS[0] + SEP_1 + TM_FLAGS[1]:<{WIDTH}}[float,float] a min and max melting temp (Tm) specified as a comma separated list{DEF_OPEN}{Parameters._DEF_MIN_TM}{SEP_3}{Parameters._DEF_MAX_TM}{CLOSE}{EOL}" + \
                       f"{GAP}{PCR_LEN_FLAGS[0] + SEP_1 + PCR_LEN_FLAGS[1]:<{WIDTH}}[int(s)] a single PCR product length or a range specified as 'min,max'{DEF_OPEN}{Parameters._DEF_MIN_PCR}{SEP_3}{Parameters._DEF_MAX_PCR}{CLOSE}{EOL}" + \
                       f"{GAP}{TM_DIFF_FLAGS[0] + SEP_1 + TM_DIFF_FLAGS[1]:<{WIDTH}}[float] the maximum allowable Tm difference between a pair of primers{DEF_OPEN}{Parameters._DEF_MAX_TM_DIFF}{CLOSE}{EOL}" + \
                       f"{GAP}{THREADS_FLAGS[0] + SEP_1 + THREADS_FLAGS[1]:<{WIDTH}}[int] the number of threads for parallel processing{DEF_OPEN}{Parameters._DEF_NUM_THREADS}{CLOSE}{EOL}" + \
                       f"{GAP}{VERSION_FLAGS[0] + SEP_1 + VERSION_FLAGS[1]:<{WIDTH}}print the version{EOL}" + \
                       f"{GAP}{HELP_FLAGS[0] + SEP_1 + HELP_FLAGS[1]:<{WIDTH}}print this message{EOL}" + \
                       f"{GAP}{DEBUG_FLAGS[0]:<{WIDTH}}run in debug mode{EOL*2}"
            
            print(HELP_MSG)
            
        # set default values
        self.ingroupFns = None
        self.outFn = None
        self.outgroupFns = Parameters._DEF_OUTGROUP
        self.disallowedLens = None # start as None; update at the end
        self.format = Parameters._DEF_FRMT
        self.minLen = Parameters._DEF_MIN_LEN
        self.maxLen = Parameters._DEF_MAX_LEN
        self.minGc = Parameters._DEF_MIN_GC
        self.maxGc = Parameters._DEF_MAX_GC
        self.minTm = Parameters._DEF_MIN_TM
        self.maxTm = Parameters._DEF_MAX_TM
        self.minPcr = Parameters._DEF_MIN_PCR
        self.maxPcr = Parameters._DEF_MAX_PCR
        self.maxTmDiff = Parameters._DEF_MAX_TM_DIFF
        self.numThreads = Parameters._DEF_NUM_THREADS
        self.debug = Parameters._DEF_DEBUG
        self.helpRequested = Parameters._DEF_HELP
        
        # give help if requested
        if HELP_FLAGS[0] in sys.argv or HELP_FLAGS[1] in sys.argv or len(sys.argv) == 1:
            self.helpRequested = True
            printHelp()
        
        # print the version if requested
        elif VERSION_FLAGS[0] in sys.argv or VERSION_FLAGS[1] in sys.argv:
            self.helpRequested = True
            print(version)
        
        # parse command line arguments
        else:
            opts,args = getopt.getopt(sys.argv[1:], SHORT_OPTS, LONG_OPTS)
            for opt,arg in opts:
                # get the ingroup filenames
                if opt in INGROUP_FLAGS:
                    self.ingroupFns = glob.glob(arg)
                    for fn in self.ingroupFns:
                        if not os.path.isfile(fn):
                            raise ValueError(ERR_MSG_1)
                    if self.ingroupFns == []:
                        raise ValueError(ERR_MSG_1)
                
                # get output filehandle
                elif opt in OUT_FLAGS:
                    # make sure the file does not exist
                    if os.path.exists(arg):
                        raise ValueError(ERR_MSG_2)
                    
                    # make sure the file can be written
                    try:
                        fh = open(arg, 'w')
                        fh.close()
                        os.remove(arg)
                    except:
                        raise ValueError(ERR_MSG_3)
                    
                    self.outFn = arg
                
                # get the outgroup filenames
                elif opt in OUTGROUP_FLAGS:
                    self.outgroupFns = glob.glob(arg)
                    for fn in self.outgroupFns:
                        if not os.path.isfile(fn):
                            raise ValueError(ERR_MSG_4)
                    if self.outgroupFns == []:
                        raise ValueError(ERR_MSG_4)
                
                # get the disallowed outgroup pcr product lengths
                elif opt in DISALLOW_FLAGS:
                    # split comma-separated list
                    disallowed = arg.split(SEP)
                    
                    # make sure exactly two values provided
                    if len(disallowed) != 2:
                        raise ValueError(ERR_MSG_5)
                    
                    # coerce lengths to ints
                    try:
                        disallowed = [int(x) for x in disallowed]
                    except:
                        raise ValueError(ERR_MSG_6)
                    
                    # save the values
                    self.disallowedLens = range(min(disallowed), max(disallowed)+1)
                
                # get the file format
                elif opt in FMT_FLAGS:
                    if arg not in Parameters._ALLOWED_FORMATS:
                        raise ValueError(ERR_MSG_7)
                    self.format = arg
                
                # get the primer lengths
                elif opt in PRIMER_LEN_FLAGS:
                    # split comma-separated list
                    primerRange = arg.split(SEP)
                    
                    # make sure at one or two primers specified
                    if len(primerRange) not in {1,2}:
                        raise ValueError(ERR_MSG_8)
                    
                    # coerce to lengths to ints
                    try:
                        primerRange = [int(x) for x in primerRange]
                    except:
                        raise ValueError(ERR_MSG_9)
                    
                    # save values
                    self.minLen = min(primerRange)
                    self.maxLen = max(primerRange)
                
                # get the allowed GC range
                elif opt in GC_FLAGS:
                    # expecting two values separated by a comma
                    gcRange = arg.split(SEP)
                    if len(gcRange) != 2:
                        raise ValueError(ERR_MSG_10)
                    
                    # make sure the values are numeric
                    try:
                        gcRange = [float(x) for x in gcRange]
                    except:
                        raise ValueError(ERR_MSG_11)
                
                    # save values
                    self.minGc = min(gcRange)
                    self.maxGc = max(gcRange)
                
                # get the allowed Tm range
                elif opt in TM_FLAGS:
                    # expecting two values separated by a comma
                    tmRange = arg.split(SEP)
                    if len(tmRange) != 2:
                        raise ValueError(ERR_MSG_12)
                
                    # make sure the values are numeric
                    try:
                        tmRange = [float(x) for x in tmRange]
                    except:
                        raise ValueError(ERR_MSG_13)
                
                    # save values
                    self.minTm = min(tmRange)
                    self.maxTm = max(tmRange)
            
                # get the allowed PCR lengths
                elif opt in PCR_LEN_FLAGS:
                    # expecting one or two values
                    pcrRange = arg.split(SEP)
                    if len(pcrRange) not in {1,2}:
                        raise ValueError(ERR_MSG_14)
                    
                    # coerce to integers
                    try:
                        pcrRange = [int(x) for x in pcrRange]
                    except:
                        raise ValueError(ERR_MSG_15)
                
                    # save values
                    self.minPcr = min(pcrRange)
                    self.maxPcr = max(pcrRange)
                    
                    # see if the disallowed needs to be changed
                    if self.disallowedLens is None:
                        self.disallowedLens = range(self.minPcr,self.maxPcr+1)
                
                # get the allowed Tm difference between primer pairs
                elif opt in TM_DIFF_FLAGS:
                    # make sure input is numeric
                    try:
                        self.maxTmDiff = float(arg)
                    except:
                        raise ValueError(ERR_MSG_16)
                
                # get the number of threads to use
                elif opt in THREADS_FLAGS:
                    # make sure input is an integer
                    try:
                        self.numThreads = int(arg)
                    except:
                        raise ValueError(ERR_MSG_17)
                
                elif opt in DEBUG_FLAGS:
                    self.debug = True
                
                else:
                    print(IGNORE_MSG + opt + " " + arg)
            
            # update disallowed to match pcr parameters unless it was already specified
            if self.disallowedLens is None:
                self.disallowedLens = range(self.minPcr, self.maxPcr + 1)
            
            # make sure an input file was specified
            if self.ingroupFns is None:
                raise ValueError(ERR_MSG_18)
            
            # make sure an output file was specified
            if self.outFn is None:
                raise ValueError(ERR_MSG_19)
    
    def logRunDetails(self, version) -> None:
        """saves the details for the current instance of the program
        """
        # constant
        WIDTH = 34
        
        # write the parameters to the log file
        self.log.debug(f'{"version:":<{WIDTH}}{version}')
        self.log.debug(f'{"ingroup:":<{WIDTH}}{",".join(self.ingroupFns)}')
        self.log.debug(f'{"outgroup:":<{WIDTH}}{",".join(self.outgroupFns)}')
        self.log.debug(f'{"out filename:":{WIDTH}}{self.outFn}')
        self.log.debug(f'{"file format:":{WIDTH}}{self.format}')
        self.log.debug(f'{"min kmer len:":{WIDTH}}{self.minLen}')
        self.log.debug(f'{"max kmer len:":<{WIDTH}}{self.maxLen}')
        self.log.debug(f'{"min % G+C":<{WIDTH}}{self.minGc}')
        self.log.debug(f'{"max % G+C":<{WIDTH}}{self.maxGc}')
        self.log.debug(f'{"min Tm:":<{WIDTH}}{self.minTm}')
        self.log.debug(f'{"max Tm:":<{WIDTH}}{self.maxTm}')
        self.log.debug(f'{"max Tm difference:":<{WIDTH}}{self.maxTmDiff}')
        self.log.debug(f'{"min PCR size:":<{WIDTH}}{self.minPcr}')
        self.log.debug(f'{"max PCR size:":<{WIDTH}}{self.maxPcr}')
        self.log.debug(f'{"disallowed outgroup PCR sizes:":<{WIDTH}}{"-".join(map(str,[min(self.disallowedLens),max(self.disallowedLens)]))}')
        self.log.debug(f'{"num threads:":<{WIDTH}}{self.numThreads}')
    
    def dumpObj(self, obj:any, fn:str, objName:str) -> None:
        """dumps an object in memory to file as a pickle

        Args:
            obj (any): the object to dump
            fn (str): the filename where object will be dumped
            objName (str): the name of the dumped object
        """
        fn = os.path.join(self.log.debugDir, fn)
        with open(fn, 'wb') as fh:
            pickle.dump(obj, fh)
        
        self.log.debug(f"dumped {objName} to {fn}")