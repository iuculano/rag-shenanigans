from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.joiners import DocumentJoiner
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever, PgvectorKeywordRetriever
from haystack_integrations.components.rankers.jina import JinaRanker

from components.markdown_splitter import MarkdownDocumentSplitter
from components.markdown_cleaner import MarkdownDocumentCleaner
from glob import glob
from typing import Dict, Any


import concurrent.futures
from haystack.components.generators import OpenAIGenerator

RELEVANT_QUOTE_PROMPT='''
You are an expert research assistant.

You will be provided a document. From the document, you must:
1. Identify the quotes that best answer the question asked, OR
2. Provide relevant context

Your findings should be returned in a list.
Do not provide any other commentary.

<document>
{chunk}
</document>
'''

FINAL_QUESTION_PROMPT='''
You are an expert research assistant.

You will be provided:
1. A series of quotes.
2. A question.

The quotes have already been filtered and determined to be relevant to the question.

Using the quotes, answer the question to the best of your ability.
If you feel that you cannot provide a clear, definitive answer, say you are unsure instead.

<quotes>
{quotes}
</quotes>

<question>
{query}
</question>
'''

class ReconstructiveRetriever():
    '''
    Wrapper around document loading and indexing.

    1. Loads documents for text searches.
    2. Loads documents for vector searches.ocument_s
    '''

    def __init__(self,
        document_store: PgvectorDocumentStore,
        inquery_embedder_model: str = 'text-embedding-3-small',
        quote_helper_model: str     = 'gpt-4o-mini',
        final_output_model: str     = 'gpt-4o',
        skip_reconstruction: bool   = True,
        
    ):
        self._document_store         = document_store
        self._inquery_embedder_model = inquery_embedder_model
        self._quote_helper_model     = quote_helper_model
        self._final_output_model     = final_output_model
        self._skip_reconstruction    = skip_reconstruction
        
        self._openai_text_client = OpenAIGenerator(model=quote_helper_model)
        self._query_pipeline     = self._setup_initial_query_pipeline()

    def _setup_initial_query_pipeline(self):
        text_embedder       = OpenAITextEmbedder(model=self._inquery_embedder_model, dimensions=512)
        embedding_retriever = PgvectorEmbeddingRetriever(document_store=self._document_store, vector_function='cosine_similarity')
        bm25_retriever      = PgvectorKeywordRetriever(document_store=self._document_store)
        document_joiner     = DocumentJoiner()
        ranker              = JinaRanker()

        query_pipeline = Pipeline()

        query_pipeline.add_component('text_embedder', text_embedder)
        query_pipeline.add_component('embedding_retriever', embedding_retriever)
        query_pipeline.add_component('bm25_retriever', bm25_retriever)
        query_pipeline.add_component('document_joiner', document_joiner)
        query_pipeline.add_component('ranker', ranker)

        query_pipeline.connect('text_embedder.embedding', 'embedding_retriever.query_embedding')
        query_pipeline.connect('embedding_retriever', 'document_joiner')
        query_pipeline.connect('bm25_retriever', 'document_joiner')        
        query_pipeline.connect('document_joiner', 'ranker')

        return query_pipeline

    def _dedupe_ranked_results(self, ranked_results: Dict[str, Any]):
        # Dedupe section spans for retrieved chunks
        # This should probably be a component
        deduped_sections = {}
        for document in ranked_results['ranker']['documents']:
            identifer = document.meta['section_id']
            name      = document.meta['document_name']
            start     = document.meta['reconstruction_start_index']
            end       = document.meta['reconstruction_end_index']
            section   = document.meta['section_name']
            content   = document.content

            if identifer not in deduped_sections:
                # End is static, it's always the end of the section
                deduped_sections[identifer] = {
                    'name':    name,
                    'section': section,
                    'content': content,
                    'start':   start, 
                    'end':     end
                }
            else:
                # Set the smaller value as we iterate over
                deduped_sections[identifer]['start'] = min(deduped_sections[identifer]['start'], start)

        # Todo make this more strongly typed
        return deduped_sections

    def _gather_content_slices(self, document_slice_descriptors: Dict[str, Any]):
        output = []

        for key, value in document_slice_descriptors.items():
            with open(f'files/{value["name"]}', 'r') as file:
                data  = file.read()
                chunk = data[value['start']:value['end']]

                output.append(chunk)

        return output

    def _quote_search_func(self, query: str):
        response = self._openai_text_client.run(query)
        return response['replies'][0]

    def _concurrent_quote_search(self, chunks: list[str]):
        templated_chunks = []
        for chunk in chunks:
            formatted_chunk = RELEVANT_QUOTE_PROMPT.format(chunk = chunk)
            templated_chunks.append(formatted_chunk)

        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for chunk in templated_chunks:
                futures.append(executor.submit(self._quote_search_func, chunk))

            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

            return results

    def _final_question(self, query: str, quotes: list[str]):
        question = FINAL_QUESTION_PROMPT.format(
            query  = query,
            quotes = '\n'.join(quotes) 
        )

        response = self._openai_text_client.run(question)
        return response['replies'][0]

    def run(self, query: str):
        result = self._query_pipeline.run({
            'text_embedder':  {'text':  query}, 
            'bm25_retriever': {'query': query},
            'ranker':         {'query': query}
        })

        slice_descriptors = self._dedupe_ranked_results(result)
        content_slices    = self._gather_content_slices(slice_descriptors)
        relevant_quotes   = self._concurrent_quote_search(content_slices)
        answer            = self._final_question(query, relevant_quotes)
        test = 1


    def _lookup_document(self, file_path: str):
        pass
