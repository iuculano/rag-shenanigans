import asyncio
import mimetypes

import fsspec
from haystack import component, Document
from haystack.dataclasses.byte_stream import ByteStream
from typing   import List, Optional

@component
class ByteArrayAdapter():
    '''
    Asynchronously reads files identified by URIs and converts them into
    Haystack Documents.
    '''
    def __init__(self) -> None:
        '''Initializes the ByteArrayAdapter.'''
        pass

    @component.output_types(streams=List[ByteStream])
    def run(self, sources: List[str]):
        '''

        '''

        file_uris = file_uris
        raise NotImplementedError('Use run_async for asynchronous I/O operations.')

    @component.output_types(streams=List[ByteStream])
    async def run_async(self, sources: List[str]):
        # Early exit if nothing was provided
        if not sources:
            return {'documents': []}

        # Create a list of tasks, one for each URI processing coroutine
        tasks   = [self._create_document_async(uri) for uri in sources]
        results = await asyncio.gather(*tasks)

        # Filter out any None results (which indicate an error for that URI)
        documents = [doc for doc in results if doc is not None]
        return {
            'documents': documents
        }

    async def _create_document_async(self, uri: str) -> Optional[ByteStream]:
        """
        Internal helper coroutine to create a single Document from a URI asynchronously.
        Uses fsspec to handle various filesystem protocols.
        """

        fs, path = fsspec.core.url_to_fs(uri, asynchronous = True)

        # Try to figure out of it actually exists
        if not fs.exists(path) or not fs.isfile(path):
            return None

        # 3. Asynchronously open and read the file content
        with fs.open(path, mode='rb') as file:
            data = file.read()

        # 4. Determine MIME type and prepare metadata
        mime_type = mimetypes.guess_type(uri)
        metadata  = {
            'source_uri':      uri,
            'size':            len(data),
            'filesystem_type': type(fs).__name__
        }
        
        stream = ByteStream(
            data      = data, 
            meta      = metadata, 
            mime_type = mime_type
        )

        return stream

