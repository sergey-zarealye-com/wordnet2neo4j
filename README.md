# Description

Script was designed for uploading wordnet files into neo4j database.
Initially it was made by @sergeypid in 2015. It was fixed for modern 
versions of *python*, *neo4j*, *py2neo* in 2020. Now it works with:

* neo4j 4.0.*
* py2neo 4.3+
* python 3+

Original paper (in Russian) about how to use Neo4j with Russian version of
Wordent was published [here](https://habr.com/ru/post/273241/). However, one
can use these the scripts with classic English version of Wordnet as well.

# Install & Run

Be sure that you have working *neo4j* community server. Install it to either
your main system or into separate server. You may install it with docker image
or directly. Check connection via browser: 
* open http://1.2.3.4:7474/browser
* :server connect
* type `bolt://1.2.3.4:7687` into address field your connection data (maybe neo4j/neo4j)
* check the query `MATCH (e) RETURN e`

If it works OK, you can move to installing wordnet filling scripts to your
computer.

`pip3 install py2neo
wget http://wordnetcode.princeton.edu/wn3.1.dict.tar.gz
tar -xzf wn3.1.dict.tar.gz
git clone https://github.com/comcon1/wordnet2neo4j
wordnet2neo4j/wordnet2neo4j.py -i dict/data.noun --neo4j bolt://1.2.3.4:7687 \
  --nodelabel Enwordnet --reltype Pointer --limit 1000 --password your_pass`

*Have a nice read!*
