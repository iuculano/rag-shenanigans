from haystack import component, Document
from typing import List

@component
class ReconstructedDocumentContentFetcher:
    '''
    For better or worse, fetches substrings from document content stored in a
    database.
    '''

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        output = []

        for document in documents:

            # Dedupe section spans for retrieved chunks
            deduped_sections = {}
            for document in result['ranker']['documents']:
                identifer = document.meta['section_id']
                name      = document.meta['document_name']
                start     = document.meta['reconstruction_start_index']
                end       = document.meta['reconstruction_end_index']
                section   = document.meta['section_name']
                content   = document.content

    
            if identifer not in result:
                # End is static, it's always the end of the section
                deduped_sections[identifer] = {
                    'name': name,
                    'section': section,
                    'content': content,
                    'start': start, 
                    'end': end
                }
            else:
                # Set the smaller value as we iterate over
                deduped_sections[identifer]['start'] = min(result[identifer]['start'], start)