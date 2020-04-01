# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 15:03:08 2015
@author: sergey, comcon1

Example usage:

NOUNS
-i dict/data.noun --neo4j bolt://127.0.0.1:7687 --nodelabel Enwordnet --reltype Pointer --limit 1000

VERBS
-i dict/data.verb --neo4j bolt://127.0.0.1:7687 --nodelabel Enwordnet --reltype Pointer --limit 1000

"""

import argparse
import re, sys

from neo4jstuff import StuffNeo4j

def main(argv):
    parser = argparse.ArgumentParser(description=
        "Parses WordNet database. Stores the results in neo4j dtabase/")   
    parser.add_argument(
        "--neo4j", required=True,
        help="URI string for connection to neo4j database, e.g. 'bolt://127.0.0.1:7687'."
    )
    parser.add_argument(
            "--password", required=False,
            help="Password for neo4j user for connection to DB."
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
        "--limit", default=sys.maxsize, type=int,
        help="Maximum number of lines to process in input file, for debugging."
    )
    parser.add_argument(
        "--encoding", 
        help="Wordnet data file encoding e.g. cp1251."
    )
    
    args = parser.parse_args()    
    
    # Initialize params
    the = StuffNeo4j(args.nodelabel, args.reltype)
    
    # Connect to DB
    if args.password is None:
        the.connect(args.neo4j)    
    else:
        the.connect(args.neo4j, pwd=args.password)    


    entry_pattern = re.compile(r'(\d{8,8}) \d\d (\w) \d\d (\w+) ')
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
                print( "%d/%d words inserted" % (len(dictionary), cnt) )
                dictionary = []
            if cnt > args.limit:
                break
    the.insert_bulk(dictionary)
    the.create_indexes()
    
    #TODO we only add relations to existing nodes!
    pointer_pattern = re.compile(r'([@!;~i#msp%=+-cru<\^>*]{1,2} \d{8,8} \w)')
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
                            print( "%d/%d relations inserted" % \
                                    (len(relations), cnt) )
                            relations = []
            if cnt > args.limit:
                break
    the.insert_bulk(relations)
    
if __name__ == '__main__':
    main(sys.argv)
