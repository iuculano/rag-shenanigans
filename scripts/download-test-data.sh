#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

mkdir -p $PARENT_DIR/files
rm -rf $PARENT_DIR/files
cd "$PARENT_DIR"

mkdir -p /tmp/test-data
rm -rf /tmp/test-data
git clone https://github.com/awsdocs/amazon-eks-user-guide.git /tmp/test-data
cp -r /tmp/test-data/doc_source/. $PARENT_DIR/files/
