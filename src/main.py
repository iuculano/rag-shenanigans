from core import Indexer
from core import ReconstructiveRetriever

# Seemingly needed for notebooks to function correctly
# import nest_asyncio
# nest_asyncio.apply()


indexer = Indexer('aws_rag_test', 
    recreate_tables = True,
    skip_clean_pass = True
)

indexer.run('data/files/*.md')

#retriever = ReconstructiveRetriever(indexer.document_store)
#retriever.run('What is Karpenter?')
