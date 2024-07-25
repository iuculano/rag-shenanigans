from sqlalchemy import create_engine, func, select, inspect, Table, Column, Integer, Text, DateTime, MetaData, Index
from datetime import datetime, timezone

from haystack import component, Document
from haystack.document_stores.types.protocol import Protocol
from haystack.utils.auth import Secret
from typing import List, Dict, Any, Optional


class PostgresReconstructableDocumentStore(Protocol):
    '''
    For better or worse, fetches substrings from document content stored in a
    Postgres database.
    '''
    _engine   = None
    _metadata = None
    _table    = None

    def __init__(self,
        connection_string: Secret = Secret.from_env_var('PG_CONN_STR'),
        table_name: str           = 'reconstructable_documents',
        index_name: str           = 'reconstructable_documents_index',
        recreate_table: bool      = False
    ) -> None:
        
        postgress_str  = str(connection_string.resolve_value()).replace('postgresql', 'postgresql+psycopg')
        self._engine   = create_engine(postgress_str)
        self._metadata = MetaData()

        self._create_table(
            table_name     = table_name,
            index_name     = index_name,
            recreate_table = recreate_table
        )

    def _create_table(self, table_name: str, index_name: str, recreate_table: bool):
        table_exists = inspect(self._engine).has_table(table_name)
        index_exists = inspect(self._engine).has_index(table_name, index_name)

        table = Table(
            table_name,
            self._metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('file_name', Text),
            Column('content', Text),
            Column('created_time', DateTime, default=datetime.now(timezone.utc)),
            Column('updated_time', DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
        )

        if table_exists:
            if recreate_table:
                table.drop(self._engine)
                self._metadata.clear()

        else:
            table.create(self._engine)
            self._table = table

        # Create a hash index for the primary key so we don't grow the lookup
        # time as documents are inserted into it - it should be constant time
        index = Index(
            index_name, 
            table.c.file_name, 
            postgresql_using = 'hash'
        )

        if index_exists:
            if recreate_table:
                index.drop(table_name, index_name)

        else:
            index.create(self._engine)


    # DocumentStore interface bits
    def to_dict(self) -> Dict[str, Any]:
        '''
        Serializes this store to a dictionary.
        '''
        pass

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PostgresReconstructableDocumentStore':
        '''
        Deserializes the store from a dictionary.
        '''
        pass

    def count_documents(self) -> int:
        '''
        Returns the number of documents stored.
        '''
        statement = select([func.count()]).select_from(self._table)

        with self._engine.connect() as connection:
            result    = connection.execute(statement)
            row_count = result.scalar()
            return row_count

    def filter_documents(self, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        '''
        Returns the documents that match the filters provided.
        '''
        

    def write_documents(self, documents: List[Document], policy: DuplicatePolicy = DuplicatePolicy.FAIL) -> int:
        """
        Writes (or overwrites) documents into the DocumentStore, return the number of documents that was written.
        """

    def delete_documents(self, document_ids: List[str]) -> None:
        """
        Deletes all documents with a matching document_ids from the DocumentStore.
        """