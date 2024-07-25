import os
import re
import uuid
from haystack import component, Document
from typing import List, Callable

from dataclasses import dataclass, asdict
from typing import List

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdformat.renderer import MDRenderer

md = MarkdownIt("commonmark")

source_markdown = """
Here's some *text*

1. a list

> a *quote*"""



@dataclass
class Metadata:
    file_name: str
    section_id: str
    content_start_index: int
    content_end_index: int

class Chunk():
   def __init__(self, content: str, meta: Metadata):
      self._content = content
      self._meta = meta

class Markdown():
    def __init__(self):
        self._markdown = MarkdownIt('commonmark').enable('table')

        self._content: str
        self._chunk_list: list[Chunk] = []
        self._render_functions = {}

        self._add_render_function('inline', self._render_inline)
        self._add_render_function('text', self._render_text)
        self._add_render_function('html_inline', self._render_text)
        self._add_render_function('heading_open', self._render_heading_open)
        self._add_render_function('heading_close', self._render_newline)
        self._add_render_function('strong_open', self._render_strong_open)
        self._add_render_function('strong_close', self._render_strong_close)
        self._add_render_function('paragraph_open', self._render_newline)
        self._add_render_function('paragraph_close', self._render_newline)
       # self._add_render_function('text', self._render_text)

    def _add_render_function(self, name: str, function) -> None:
        self._render_functions[name] = function

    def _get_render_function(self, name: str):
        return self._render_functions[name]

    def _render_inline(self, token):
        buffer = ''
        for child in token.children:
            func = self._get_render_function(child.type)
            data = func(child)

            buffer += data
        
        return buffer
    
    def _render_

    def _render_text(self, token) -> str:
        return token.content

    def _render_heading_open(self, token) -> str:
        return f'{token.markup} '

    def _render_newline(self, token) -> str:
        return '\n'
    
    def clean(self, content: str) -> None:
        tokens = self._markdown.parse(content)
        buffer = ''

        for token in tokens:
            func = self._get_render_function(token.type)
            data = func(token)

            buffer += data
            test = 1

@component
class CustomMarkdownDocumentCleaner:
  def __init__(self, table_delimiter='|'):
        self._table_delimiter = table_delimiter

  @component.output_types(documents=List[Document])
  def run(self, documents: List[Document]):
    markdown = Markdown()

    for doc in documents:
        data = doc.content
        markdown.clean(data)
        