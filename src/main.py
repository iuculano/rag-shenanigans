from core import Indexer
from core import ReconstructiveRetriever


indexer = Indexer('aws_rag_test', 
    recreate_tables = False,
    skip_clean_pass = True
)
#indexer.run('files/*.md')

retriever = ReconstructiveRetriever(indexer.document_store)
retriever.run('What is Karpenter?')
# ParallelReconstructiveRetreiver()
#
#
#

#
#retriever = PgvectorKeywordRetriever(document_store=document_store)
#data = retriever.run(query='What is Karpenter')
#
#text_embedder = OpenAITextEmbedder(model='text-embedding-3-small')
#embedding_retriever = PgvectorEmbeddingRetriever(document_store=document_store, vector_function='cosine_similarity')
#bm25_retriever = PgvectorKeywordRetriever(document_store=document_store)
#document_joiner = DocumentJoiner()
#ranker = JinaRanker()
#
#query_pipeline = Pipeline()
#query_pipeline.add_component('text_embedder', text_embedder)
#query_pipeline.add_component('embedding_retriever', embedding_retriever)
##query_pipeline.add_component('bm25_retriever', bm25_retriever)
#query_pipeline.add_component('document_joiner', document_joiner)
#query_pipeline.add_component('ranker', ranker)
#
#query_pipeline.connect('text_embedder.embedding', 'embedding_retriever.query_embedding')
##query_pipeline.connect('bm25_retriever', 'document_joiner')
#query_pipeline.connect('embedding_retriever', 'document_joiner')
#query_pipeline.connect('document_joiner', 'ranker')
#
#query = 'What is Karpenter?'
#
#result = query_pipeline.run({
#    'text_embedder': {'text': query}, 
#    #'bm25_retriever': {'query': query},
#    'ranker': {'query': query}
#})
#
#test = 1
#
#
#

#
## capacity blocks is missing part of the vector
#print(result['retriever']['documents'][0])
##