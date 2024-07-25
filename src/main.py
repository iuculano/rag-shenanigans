from core import Indexer
from core import ReconstructiveRetriever


indexer = Indexer('aws_rag_test', 
    recreate_tables = False,
    skip_clean_pass = True
)
#indexer.run('files/*.md')

retriever = ReconstructiveRetriever(indexer.document_store)
retriever.run('What is Karpenter?')
