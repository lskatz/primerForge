import unittest
from Bio.Seq import Seq
from bin.Primer import Primer
from Bio.SeqUtils import MeltingTemp

class PrimerTest(unittest.TestCase):
    """unit tests for evaluating the Primer class
    """
    # constants
    FWD_SEQ = "agagtttgatcctggctcag"
    REV_SEQ = "ggttaccttgttacgactt"
    CNTG_1 = "contig 1"
    CNTG_2 = "contig 2"
    FSTR_1 = 4
    FSTR_2 = 8
    FEND_1 = 23
    FEND_2 = 27
    RSTR_1 = 300
    RSTR_2 = 666
    REND_1 = 318
    REND_2 = 684
    
    def setUp(self) -> None:
        # make primer objects
        self.fwd_1 = Primer(PrimerTest.FWD_SEQ, PrimerTest.CNTG_1, PrimerTest.FSTR_1, len(PrimerTest.FWD_SEQ))
        self.fwd_2 = Primer(PrimerTest.FWD_SEQ, PrimerTest.CNTG_2, PrimerTest.FSTR_2, len(PrimerTest.FWD_SEQ))
        self.rev_1 = Primer(PrimerTest.REV_SEQ, PrimerTest.CNTG_1, PrimerTest.RSTR_1, len(PrimerTest.REV_SEQ))
        self.rev_2 = Primer(PrimerTest.REV_SEQ, PrimerTest.CNTG_2, PrimerTest.RSTR_2, len(PrimerTest.REV_SEQ))
    
    def tearDown(self) -> None:
        pass
    
    def _getGc(seq:Seq) -> float:
        seq = str(seq.upper())
        numGc = len(seq.replace('A', '').replace('T', ''))
        return numGc / len(seq) * 100
    
    def testA_isSeq(self) -> None:
        """is sequence Seq object
        """
        # make sure the stored sequences are Seq
        self.assertIsInstance(self.fwd_1.seq, Seq)
        self.assertIsInstance(self.fwd_2.seq, Seq)
        self.assertIsInstance(self.rev_1.seq, Seq)
        self.assertIsInstance(self.rev_2.seq, Seq)
    
    def testB_isSeqCapital(self) -> None:
        """is sequence capitalized
        """
        # make sure the sequences are capitalized
        self.assertEqual(self.fwd_1.seq, Seq(PrimerTest.FWD_SEQ.upper()))
        self.assertEqual(self.fwd_2.seq, Seq(PrimerTest.FWD_SEQ.upper()))
        self.assertEqual(self.rev_1.seq, Seq(PrimerTest.REV_SEQ.upper()))
        self.assertEqual(self.rev_2.seq, Seq(PrimerTest.REV_SEQ.upper()))
    
    def testC_equality(self) -> None:
        """is equality based on sequence only
        """
        # make sure objects with shared sequences are equal
        self.assertEqual(self.fwd_1, self.fwd_1)
        self.assertEqual(self.fwd_1, self.fwd_2)
        self.assertEqual(self.rev_1, self.rev_1)
        self.assertEqual(self.rev_1, self.rev_2)
    
    def testD_inequality(self) -> None:
        """is inequality based on sequence only
        """
        # make sure objects with different sequences are not equal
        self.assertNotEqual(self.fwd_1, self.rev_1)
        self.assertNotEqual(self.fwd_1, self.rev_2)
        self.assertNotEqual(self.fwd_2, self.rev_1)
        self.assertNotEqual(self.fwd_2, self.rev_2)
    
    def testE_start(self) -> None:
        """is the start position accurate
        """
        # make sure the start is stored correctly
        self.assertEqual(self.fwd_1.start, PrimerTest.FSTR_1)
        self.assertEqual(self.fwd_2.start, PrimerTest.FSTR_2)
        self.assertEqual(self.rev_1.start, PrimerTest.RSTR_1)
        self.assertEqual(self.rev_2.start, PrimerTest.RSTR_2)

    def testF_end(self) -> None:
        """is the end position accurate
        """
        # make sure the end is stored correctly
        self.assertEqual(self.fwd_1.end, PrimerTest.FEND_1)
        self.assertEqual(self.fwd_2.end, PrimerTest.FEND_2)
        self.assertEqual(self.rev_1.end, PrimerTest.REND_1)
        self.assertEqual(self.rev_2.end, PrimerTest.REND_2)
    
    def testG_length(self) -> None:
        """is `len` working?
        """
        # make sure the length is correct
        self.assertEqual(len(self.fwd_1), len(PrimerTest.FWD_SEQ))
        self.assertEqual(len(self.fwd_2), len(PrimerTest.FWD_SEQ))
        self.assertEqual(len(self.rev_1), len(PrimerTest.REV_SEQ))
        self.assertEqual(len(self.rev_2), len(PrimerTest.REV_SEQ))
    
    def testH_meltingTemp(self) -> None:
        """is the meltiing temperature accurate
        """
        # constants
        FWD_TM = MeltingTemp.Tm_Wallace(PrimerTest.FWD_SEQ)
        REV_TM = MeltingTemp.Tm_Wallace(PrimerTest.REV_SEQ)
        
        # make sure Tm is calculated correctly
        self.assertAlmostEqual(self.fwd_1.Tm, FWD_TM)
        self.assertAlmostEqual(self.fwd_2.Tm, FWD_TM)
        self.assertAlmostEqual(self.rev_1.Tm, REV_TM)
        self.assertAlmostEqual(self.rev_2.Tm, REV_TM)
    
    def testI_gcPercent(self) -> None:
        """is the % GC accurate
        """
        # constants
        FWD_GC = PrimerTest._getGc(PrimerTest.FWD_SEQ)
        REV_GC = PrimerTest._getGc(PrimerTest.REV_SEQ)
        
        # make sure % GC is calculated correctly
        self.assertAlmostEqual(self.fwd_1.gcPer, FWD_GC)
        self.assertAlmostEqual(self.fwd_2.gcPer, FWD_GC)
        self.assertAlmostEqual(self.rev_1.gcPer, REV_GC)
        self.assertAlmostEqual(self.rev_2.gcPer, REV_GC)
    
    def testJ_minimizer(self) -> None:
        """is `getMinimizer` working
        """
        # constants
        FWD_MIN_10 = Seq('AGAGTTTGAT')
        FWD_MIN_6  = Seq('AGAGTT')
        REV_MIN_10 = Seq('ACCTTGTTAC')
        REV_MIN_6  = Seq('ACCTTG')
        
        # make sure the minimizer sequences are calculated correctly
        self.assertEqual(self.fwd_1.getMinimizer(10), FWD_MIN_10)
        self.assertEqual(self.fwd_2.getMinimizer(10), FWD_MIN_10)
        self.assertEqual(self.rev_1.getMinimizer(10), REV_MIN_10)
        self.assertEqual(self.rev_2.getMinimizer(10), REV_MIN_10)
        self.assertEqual(self.fwd_1.getMinimizer(6),  FWD_MIN_6)
        self.assertEqual(self.fwd_2.getMinimizer(6),  FWD_MIN_6)
        self.assertEqual(self.rev_1.getMinimizer(6),  REV_MIN_6)
        self.assertEqual(self.rev_2.getMinimizer(6),  REV_MIN_6)
    
    def testK_string(self) -> None:
        """is `str` producing the sequence as a string
        """
        # make sure the string function is working correctly
        self.assertEqual(str(self.fwd_1), str(PrimerTest.FWD_SEQ))
        self.assertEqual(str(self.fwd_2), str(PrimerTest.FWD_SEQ))
        self.assertEqual(str(self.rev_1), str(PrimerTest.REV_SEQ))
        self.assertEqual(str(self.rev_2), str(PrimerTest.REV_SEQ))

    def testL_contig(self) -> None:
        """is the contig stored properly
        """
        # make sure the contigs are being stored correctly
        self.assertEqual(self.fwd_1.contig, PrimerTest.CNTG_1)
        self.assertEqual(self.fwd_2.contig, PrimerTest.CNTG_2)
        self.assertEqual(self.rev_1.contig, PrimerTest.CNTG_1)
        self.assertEqual(self.rev_2.contig, PrimerTest.CNTG_2)
