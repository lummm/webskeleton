#!/bin/bash


export KEY="test-key"
export PGPASSWORD="test-db-pw"
export PORT="0"

set -e
for f in $(find ./test -name '*.test.py'); do
    python3.9 $f
done
