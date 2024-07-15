from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from preprocessor import CustomDocumentSplitter
from glob import glob

document_store = InMemoryDocumentStore(embedding_similarity_function='cosine')

indexing_pipeline = Pipeline()
indexing_pipeline.add_component('text_file_converter', TextFileToDocument())
indexing_pipeline.add_component('splitter', CustomDocumentSplitter())
indexing_pipeline.add_component('embedder', OpenAIDocumentEmbedder(meta_fields_to_embed=['document_name', 'reconstruction_start_index', 'reconstruction_end_index']))
indexing_pipeline.add_component('writer', DocumentWriter(document_store=document_store))
indexing_pipeline.connect('text_file_converter.documents', 'splitter.documents')
indexing_pipeline.connect('splitter.documents', 'embedder.documents')
indexing_pipeline.connect('embedder.documents', 'writer.documents')

files = glob('files/*.md')
indexing_pipeline.run({'text_file_converter': {'sources': files}})

query_pipeline = Pipeline()
query_pipeline.add_component('text_embedder', OpenAITextEmbedder())
query_pipeline.add_component('retriever', InMemoryEmbeddingRetriever(document_store=document_store))
query_pipeline.connect('text_embedder.embedding', 'retriever.query_embedding')

query = 'What is Karpenter?'

result = query_pipeline.run({'text_embedder': {'text': query}})

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
