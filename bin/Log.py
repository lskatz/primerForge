from __future__ import annotations
import logging, os

class Log():
    """class for interacting with the logger 
    """
    # global constants
    __LOG_DIR = "_debug"
    __LOG_FN = "primerForge.log"
    
    def __init__(self, debugDir:str='') -> Log:
        """creates a Log object

        Returns:
            Log: a Log object
        """
        # type hint attributes
        self.__logger:logging.Logger
        
        # set the debug directory
        if debugDir == '':
            self.debugDir:str = os.path.join(os.getcwd(), Log.__LOG_DIR)
        else:
            self.debugDir = debugDir
        
        # set the log file
        self.logFn:str = os.path.join(self.debugDir, Log.__LOG_FN)
    
    def initialize(self, name:str) -> None:
        """initializes the log

        Args:
            name (str): the name of the logger
        """
        # make sure debug directory exists
        if not os.path.isdir(self.debugDir):
            os.mkdir(self.debugDir)
        
        # point the log at the log file; level is debug
        logging.basicConfig(filename=self.logFn, level=logging.DEBUG)
        
        # start up the logger
        self.__logger = logging.getLogger(name)
    
    def rename(self, name:str):
        """renames the logger

        Args:
            name (str): the new name of the logger
        """
        self.__logger = logging.getLogger(name)
    
    def info(self, msg:str) -> None:
        """writes message as logger.info

        Args:
            msg (str): the message to write
        """
        self.__logger.info(msg)
    
    def debug(self, msg:str) -> None:
        """writes message as logger.debug

        Args:
            msg (str): the message to write
        """
        self.__logger.debug(msg)
    
    def error(self, msg:str) -> None:
        """writes message as logger.error

        Args:
            msg (str): the message to write
        """
        self.__logger.error(msg)
    
    def critical(self, msg:str) -> None:
        """writes message as logger.critical

        Args:
            msg (str): the message to write
        """
        self.__logger.critical(msg)
