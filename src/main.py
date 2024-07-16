from haystack import Pipeline
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack.components.caching import CacheChecker
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter
from haystack.components.joiners import DocumentJoiner
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder
from haystack_integrations.components.rankers.jina import JinaRanker
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever, PgvectorKeywordRetriever
from preprocessor import CustomDocumentSplitter
from glob import glob

# document_store = InMemoryDocumentStore(embedding_similarity_function='cosine')
document_store = PgvectorDocumentStore(
    embedding_dimension=1536,
    vector_function='cosine_similarity',
    recreate_table=False,
    search_strategy='hnsw',
)

embedding_pipeline = Pipeline()
#embedding_pipeline.add_component(instance=CacheChecker(document_store, cache_field='document_name'), name='cache_checker')
embedding_pipeline.add_component('text_file_converter', TextFileToDocument())
embedding_pipeline.add_component('splitter', CustomDocumentSplitter())
embedding_pipeline.add_component('embedder', OpenAIDocumentEmbedder(model='text-embedding-3-small', meta_fields_to_embed=['document_name', 'reconstruction_start_index', 'reconstruction_end_index']))
embedding_pipeline.add_component('writer', DocumentWriter(document_store=document_store))
#embedding_pipeline.connect('cache_checker.misses', 'text_file_converter.sources')
embedding_pipeline.connect('text_file_converter.documents', 'splitter.documents')
embedding_pipeline.connect('splitter.documents', 'embedder.documents')
embedding_pipeline.connect('embedder.documents', 'writer.documents')

files = glob('files/*.md')
embedding_pipeline.run({'text_file_converter': {'sources': files}})
retriever = PgvectorKeywordRetriever(document_store=document_store)
data = retriever.run(query='What is Karpenter')

text_embedder = OpenAITextEmbedder(model='text-embedding-3-small')
embedding_retriever = PgvectorEmbeddingRetriever(document_store=document_store, vector_function='cosine_similarity')
bm25_retriever = PgvectorKeywordRetriever(document_store=document_store)
document_joiner = DocumentJoiner()
ranker = JinaRanker()

query_pipeline = Pipeline()
query_pipeline.add_component('text_embedder', text_embedder)
query_pipeline.add_component('embedding_retriever', embedding_retriever)
query_pipeline.add_component('bm25_retriever', bm25_retriever)
query_pipeline.add_component('document_joiner', document_joiner)
query_pipeline.add_component('ranker', ranker)

query_pipeline.connect('text_embedder.embedding', 'embedding_retriever.query_embedding')
query_pipeline.connect('bm25_retriever', 'document_joiner')
query_pipeline.connect('embedding_retriever', 'document_joiner')
query_pipeline.connect('document_joiner', 'ranker')

query = 'What is Karpenter?'

result = query_pipeline.run({
    'text_embedder': {'text': query}, 
    'bm25_retriever': {'query': query},
    'ranker': {'query': query}
})

test = 1

# Dedupe section spans for retrieved chunks
deduped_sections = {}
for document in result['retriever']['documents']:
    identifer = document.meta['section_id']
    start = document.meta['reconstruction_start_index']
    end = document.meta['reconstruction_end_index']
    
    if identifer not in result:
        # End is static, it's always the end of the section
        deduped_sections[identifer] = {'start': start, 'end': end}
    else:
        # Set the smaller value as we iterate over
        deduped_sections[identifer]['start'] = min(result[identifer]['start'], start)



print(result['retriever']['documents'][0])
