# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 15:03:08 2015
@author: sergey

Example usage:

NOUNS
-i rwn3/data.noun --neo4j http://127.0.0.1:7474 --nodelabel Ruswordnet --reltype Pointer --encoding cp1251 --limit 1000

VERBS
-i rwn3/data.verb --neo4j http://127.0.0.1:7474 --nodelabel Ruswordnet --reltype Pointer --encoding cp1251 --limit 1000

"""

import sys
import argparse
import re

from neo4jstuff import StuffNeo4j

def main(argv):
    parser = argparse.ArgumentParser(description=
        "Parses WordNet database. Stores the results in neo4j dtabase/")   
    parser.add_argument(
        "--neo4j", required=True,
        help="URI string for connection to neo4j database, e.g. 'http://127.0.0.1:7474'."
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Wordnet data file e.g. dict/data.noun ."
    )
    parser.add_argument(
        "--nodelabel", required=True,
        help="Wordnet node label."
    )
    parser.add_argument(
        "--reltype", required=True,
        help="Wordnet relation type."
    )
    parser.add_argument(
        "--limit", default=sys.maxint, type=int,
        help="Maximum number of lines to process in input file, for debugging."
    )
    parser.add_argument(
        "--encoding", 
        help="Wordnet data file encoding e.g. cp1251."
    )
    
    args = parser.parse_args()    
    
    #Инициализируем параметры
    the = StuffNeo4j(args.nodelabel, args.reltype)

    #Подключаем БД
    the.connect(args.neo4j)    

    entry_pattern = re.compile(ur"(\d{8,8}) \d\d (\w) \d\d (\w+) ", re.UNICODE)
    dictionary = []
    cnt = 0
    pos = None
    with open(args.input) as wordnet:
        for raw_line in wordnet:
            if args.encoding is not None:
                line = raw_line.decode(args.encoding)
            else:
                line = raw_line
            entry = entry_pattern.findall(line)
            if len(entry):
                name = entry[0][2]
                pos = entry[0][1]
                synset_id = pos + entry[0][0]                
                word_node = the.create_node(args.nodelabel,
                                name=name,
                                synset_id=synset_id)
                dictionary.append(word_node)
            cnt += 1           
            if cnt % 100 == 0:
                the.insert_bulk(dictionary)
                print "%d/%d words inserted" % (len(dictionary), cnt)
                dictionary = []
            if cnt > args.limit:
                break
    the.insert_bulk(dictionary)
    the.create_indexes()
    
    #TODO we only add relations to existing nodes!
    pointer_pattern = re.compile("([@!;~i#msp%=+-cru<\^>*]{1,2} \d{8,8} \w)")
    cnt = 0
    relations = []
    with open(args.input) as wordnet:
        for line in wordnet:
            entry = entry_pattern.findall(line)
            if len(entry):
                name = entry[0][2]
                synset_id = entry[0][1] + entry[0][0]  
                pointers = pointer_pattern.findall(line)
                if len(pointers):
                    for pointer in pointers:
                        ptype, target, target_pos = pointer.split()
                        try:
                            rel = the.create_wordnet_rel(synset_id, 
                                                         target_pos+target, 
                                                         ptype)
                            relations.append(rel)
                        except:
                            pass
                        cnt += 1
                        if cnt % 100 == 0:
                            the.insert_bulk(relations)
                            print "%d/%d relations inserted" % (len(relations), cnt)
                            relations = []
            if cnt > args.limit:
                break
    the.insert_bulk(relations)
    
if __name__ == '__main__':
    main(sys.argv)