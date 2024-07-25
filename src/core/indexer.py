from haystack import Pipeline
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import OpenAIDocumentEmbedder
from components.markdown_splitter import MarkdownDocumentSplitter
from components.markdown_cleaner import MarkdownDocumentCleaner
from glob import glob


class Indexer():
    '''
    Wrapper around document loading and indexing.

    1. Loads documents for text searches.
    2. Loads documents for vector searches.
    '''

    def __init__(self, 
        store_name: str, 
        model_name: str          = 'text-embedding-3-small',
        embedding_dimension: int = 512,
        recreate_tables: bool    = False,
        skip_clean_pass: bool    = False
    ):
        self._store_name          = store_name
        self._model_name          = model_name
        self._embedding_dimension = embedding_dimension
        self._skip_clean_pass     = skip_clean_pass

        # Stores chunks and embeddings
        self._embedding_store = PgvectorDocumentStore(
            table_name          = f'{store_name}_embeddings',
            hnsw_index_name     = f'{store_name}_embeddings_hnsw_index',
            keyword_index_name  = f'{store_name}_embeddings_keyword_index',
            embedding_dimension = embedding_dimension,
            vector_function     = 'cosine_similarity',
            search_strategy     = 'hnsw',
            recreate_table      = recreate_tables
        )

    @property
    def document_store(self):
        return self._embedding_store

    def run(self, path: str):
        pipeline = Pipeline()
        
        pipeline.add_component('text_file_converter', TextFileToDocument())
        pipeline.add_component('cleaner', MarkdownDocumentCleaner(passthrough=self._skip_clean_pass))
        pipeline.add_component('splitter', MarkdownDocumentSplitter())        
        pipeline.add_component('embedder', OpenAIDocumentEmbedder(
            model                = self._model_name,
            dimensions           = self._embedding_dimension,
            meta_fields_to_embed = [
                'document_name',
                'reconstruction_start_index', 
                'reconstruction_end_index'
            ]
        ))
        pipeline.add_component('embedding_writer', DocumentWriter(self._embedding_store))

        # Write to both stores
        pipeline.connect('text_file_converter.documents', 'cleaner.documents')
        pipeline.connect('cleaner.documents', 'splitter.documents')
        pipeline.connect('splitter.documents', 'embedder.documents')
        pipeline.connect('embedder.documents', 'embedding_writer.documents')

        files = glob(path)
        pipeline.run({'text_file_converter': {'sources': files}})
