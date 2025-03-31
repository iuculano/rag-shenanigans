#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

rm -rf $PARENT_DIR/data

cd "$PARENT_DIR"
git clone https://github.com/awsdocs/amazon-eks-user-guide.git $PARENT_DIR/data

mkdir -p $PARENT_DIR/data/files

# honestly wtf
find ./data -type f -name "*.adoc" -not -path "./data/files/*" \
  -exec bash -c '

    # Generate the HTML files in place from .adoc
    asciidoctor -e -s -b html5 "$1"

    # Convert to markdown
    INPUT="${1%.adoc}.html"
    OUTPUT="./data/files/$(basename "$1" .adoc).md"
    pandoc -f html -t markdown "$INPUT" -o "$OUTPUT"
  ' _ {} \;
