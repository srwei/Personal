# CS121: Treemap assignment
#
# Code for building a tree from ATUS data and drawing it as a treemap.
#
################# DO NOT MODIFY THIS CODE #################

import argparse
import csv
import json
import sys

import tree
import treemap

from drawing import ColorKey

def add_category(t, code, partial_code, weight, code_to_label):
    '''
    Add category to the tree recursively.

    Inputs:
        t: (TreeNode) a tree
        code: (string) represents the rest of the time use code to add.
        partial_code: (string) prefix of the time use code that leads
          from the root to t.
        weight: (float) minutes spent on the activity
        code_to_label: (dict) maps time use codes to time use category names.
    '''

    kids = t.get_children_as_dict()
    if len(code) == 2:
        # tier 3 code.  t is a tier 2 node and we should not
        # have seen this code at this node before.
        assert code not in t._children
        complete_code = partial_code+code
        label = code_to_label.get(complete_code, "")
        t = tree.TreeNode(complete_code, label, weight)
        kids[code] = t
    else:
        # tier 1 or tier 2 sub-code
        sub_code = code[:2]
        if sub_code not in kids:
            # need to add the child for the sub_code
            # interior node, initial weight is zero
            complete_code = partial_code+sub_code
            label = code_to_label.get(complete_code, "")
            t = tree.TreeNode(partial_code+sub_code, label, 0)
            kids[sub_code] = t
        else:
            t = kids[sub_code]

        # recursively add the rest of the time code.
        add_category(t, code[2:], partial_code+sub_code, weight, code_to_label)
            

def add(t, header, participant, code_to_label):
    '''
    Add the categories with non-zero times to the tree.

    Inputs:
        header: (list of string) the names of the columns in the participant data
        participant: (list) the summary data for one participant
        code_to_label: (dict)  maps time use codes to labels
    '''

    for i in range(len(header)):
        col_name = header[i]
        if not col_name.startswith("t"):
            continue

        if int(participant[i]) <= 0:
            continue

        # found a time use code
        assert len(col_name) == 7

        # strip off the leading "t" from the code
        add_category(t, col_name[1:], "", int(participant[i]), code_to_label)


def build_tree(atus_filename, participant, code_to_label):
    '''
    Construct a tree for a specific participant or a subtree that participant.

    Inputs:
        atus_filename: (string) name of the participants data file
        participant: (integer) line number for the participant in the file

    Returns: a TreeNode
    '''

    # construct the tree
    data = [row for row in csv.reader(open(atus_filename), delimiter=",")]
    header = data[0]
    t = tree.TreeNode("", "", 0)
    if participant >= len(data):
        print("Invalid participant number:", participant, file=sys.stderr)
        sys.exit(0)

    add(t, header, data[participant], code_to_label)

    return t


def find_subtree(t, path):
    '''
    Follow a path to a subtree

    Inputs:
        t: (TreeNode) a tree
        path: (string) time code that describes the path from the root of t
            to a subtree.

    Returns: a TreeNode
    '''

    for code in [path[i:i+2] for i in range(0, len(path), 2)]:
        kids = t.get_children_as_dict()
        if code not in kids:
            print("invalid path", code, file=sys.stderr)
            return None
        t = kids[code]

    return t



def load_codes(filename="data/codes_to_labels.json"):
    '''
    Load the file that maps time codes to labels.

    Inputs: (string) filename.  Uses data/codes_to_labels.json as a
       default.

    Returns: dictionary that maps time codes (string) to labels
    (string).
    '''

    try:
        code_to_label = json.load(open(filename))
    except OSError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    return code_to_label


def load_participant(participant, 
                     code_to_label_filename=None,
                     participant_filename="data/participants.csv",
                     time_code=""):
    '''
    Load a sample participant as a tree.

    Inputs:
        participant: (int) participant's row number in participants file
        code_to_label: (dictionary) a dictionary that maps ATU codes
            to labels (loads and use "data/codes_to_labels.json" by
            default)
        participant_filename: (string) the name pf the file with the
            participant data.  (Uses "data/participants.csv" by default.)
        time_code: (string) a time code to use as a path to a subtree

    Results: a TreeNode

    Example:
      >>>  t = load_participant(1) 
      >>>  t = load_participant(1, time_code="12")
    '''

    if not code_to_label_filename:
        code_to_label = load_codes()
    else:
        code_to_label = load_codes(code_to_label_filename)
    
    t = build_tree(participant_filename,
                   participant,
                   code_to_label)

    if time_code != "":
        t = find_subtree(t, time_code)

    return t


def parse_args(args):
    '''                                                                                                                      
    Parse the arguments                                                                                                      
    '''
    parser = argparse.ArgumentParser(description='Drawing treemaps.')
    parser.add_argument('-i', '--input_filename', nargs=1, help="input filename", type=str, 
                        default=["data/participants.csv"])
    parser.add_argument('-l', '--code_to_label_filename', nargs=1, 
                        help="code to label filename", 
                        type=str, default=["data/codes_to_labels.json"])
    parser.add_argument('-o', '--output_filename', nargs=1, help="output filename", 
                        type=str, default=[None])
    parser.add_argument('-p', '--participant_row_number', nargs=1, help="participant row number", 
                        type=int, default=[1])
    parser.add_argument('-w', '--width', nargs=1, help="initial bounding rectangle height", 
                        type=float, default=[1.0])
    parser.add_argument('-c', '--time_code', nargs=1, help="time code for path to subtree", 
                        type=str, default=[""])
    

    try:
        return parser.parse_args(args[1:])
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = parse_args(sys.argv)

        participant = args.participant_row_number[0]
        if participant < 1:
            print("Invalid participant number:", participant, file=sys.stderr)
            sys.exit(0)

        # load the tree
        time_code = args.time_code[0]
        t = load_participant(participant,
                             args.code_to_label_filename[0],
                             args.input_filename[0], 
                             time_code)

        if not t:
            if time_code:
                print("Unable to load participant:", 
                      participant, 
                      "with time code:", 
                      time_code, file=sys.stderr)
            else:
                print("Unable to load participant:", 
                      participant, 
                      file=sys.stderr)
            sys.exit(1)

        # draw the treemap
        treemap.draw_treemap(t, 
                             bounding_rec_height=1.0,
                             bounding_rec_width=args.width[0],
                             output_filename=args.output_filename[0])

    else:
        print("doing nothing besides loading the code...")


