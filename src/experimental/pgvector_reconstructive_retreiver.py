from haystack import component, Document
from typing import List

from components import PostgresReconstructableDocumentStore

@component
class PgvectorReconstructiveRetriever:
    '''
    For better or worse, fetches substrings from document content stored in a
    Postgres database.
    '''

    def __init__(self,
        reconstructable_document_store: PostgresReconstructableDocumentStore
    ) -> None:
        self._reconstructable_document_store = reconstructable_document_store

    @component.output_types()
    def run(self, documents: List[Document]):
        for doc in documents:
            data = doc.content



