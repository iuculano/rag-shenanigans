import os
import re
import uuid
from nltk.tokenize.punkt import PunktSentenceTokenizer
from haystack import component, Document
from typing import List

tokenizer = PunktSentenceTokenizer()

@component
class CustomDocumentSplitter:
  @component.output_types(documents=List[Document])
  def run(self, documents: List[Document]):
    chunked_documents = []

    for doc in documents:
        data = doc.content

        # Grab the absolute position of every section
        pattern = r'^#{1,6}\s[a-zA-Z0-9-=<>/\" ]+'
        matches = re.finditer(pattern, data, re.MULTILINE)

        # Using a tuple for this is hideous
        indicies = []
        for match in matches:
            indicies.append((
               match.start(), # index of the section match
               match.end(),
               match.string[match.start():match.end()],
               uuid.uuid4().hex
            ))

        # Construct section sized chunks
        num_sections = len(indicies)
        for x in range(num_sections):
            # Generate spans of the sections
            # At the end, there's no further indicies so we just run until
            # the end of the document instead of the next index
            beg = indicies[x][0]
            end = indicies[x][0] + indicies[x + 1][0] if x < (num_sections - 1) else len(data)
            name = indicies[x][2]

            # String of the entire section
            section = data[beg:end]

            # Garbage hack around to stop NLTK from screwing up numbered lists
            pattern = re.compile(r'(\d+)(?:\.\s)')
            section = pattern.sub(r'\1) ', section)

            # Chunk by individual sentences
            # Beware this span_tokenize() call, the positions of these spans
            # is relative to the section, so we need to add its offset to move
            # it back into absolute space
            chunk_data = {}
            sentence_spans = list(tokenizer.span_tokenize(section))
            for span in sentence_spans:

                chunk_data = {
                    'content': section[span[0]:span[1]],

                    'metadata': {
                        'document_name': os.path.basename(doc.meta['file_path']),
                        'section_name': name,
                        'section_id': indicies[x][3],
                        'reconstruction_start_index': beg + span[0], # include the vector
                        'reconstruction_end_index': end,
                        'reconstruction_distance': end - (beg + span[1])
                    }
                }

                chunked_documents.append(Document(
                   content=chunk_data['content'],
                   meta=chunk_data['metadata']
                ))

    return {
       'documents': chunked_documents
    }
