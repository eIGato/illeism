# Illeism

This program is an example for learning the Machine Learning.

It uses a database and text files (example included).

The goal is to form a bag of words from target file and define the owner.

## Setup

1. Clone this repo.
2. Launch setup.sh:
```bash
./setup.sh
```

## Start

```bash
./start.sh path/to/textfile.txt --db "dbname='template1' user='dbuser' host='localhost' password='dbpass'"
# or for example without db
./start.sh textfile.example.txt
```
