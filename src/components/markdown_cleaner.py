from haystack import component, Document
from markdown_it import MarkdownIt
from mdformat.renderer import MDRenderer
from typing import List


@component
class MarkdownDocumentCleaner():
    '''
    Simple Markdown reformatter/cleaner.
    '''
    def __init__(self, passthrough: bool) -> None:
        self._markdown_parser   = MarkdownIt('commonmark')#.enable('table')
        self._markdown_renderer = MDRenderer()

        self._passthrough = passthrough

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        output: list[Document] = []

        # Provide a simple way to skip without affecting pipelines
        if self._passthrough:
            return {'documents': documents}

        for doc in documents:
            data = doc.content
            meta = doc.meta

            tokens  = self._markdown_parser.parse(data)
            content = self._markdown_renderer.render(tokens, {}, {})
            output.append(Document(content=content, meta=meta))

        return {'documents': output}
