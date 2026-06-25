import logging

logger = logging.getLogger(__name__)

class BaseMetadataComponent:
    """
    Base class for all metadata components. 
    Stores the GeminiTaskExecutor instance to avoid duplicated initialization code.
    """
    def __init__(self, executor):
        self.executor = executor
