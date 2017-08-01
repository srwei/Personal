from math import radians, cos, sin, asin, sqrt
import sqlite3
import json
import re

def query(filename, args):
    '''
    Inputs: args from the django ui as a dictionary
    Outputs: tuple (ratio_list, (heads, query_result_list))
    '''
    #fix this to account for refs2 and refs3
    if len(args) == 0:
        return
    if len(args) == 1:
        if 'comment' in args.keys():
            return
    params=[]
    if 'refs1' in args.keys():
        params.append(args['refs1'])
        if args['refs2'] != '':
            params.append(args['refs2'])
        if args['refs3'] != '':
            params.append(args['refs3'])
    if 'committing_player' in args.keys():
        params.append(args['committing_player'])
    if 'offending_team' in args.keys():
        params.append(args['offending_team'])
    if 'disadvantaged_player' in args.keys():
        params.append(args['disadvantaged_player'])
    if 'defending_team' in args.keys():
        params.append(args['defending_team'])
    if 'call_type' in args.keys():
        params.append(args['call_type'])
    if 'call_accuracy' in args.keys():
        params.append(args['call_accuracy'])
    if 'home_team' in args.keys():
        params.append(args['home_team'])
    if 'away_team' in args.keys():
        params.append(args['away_team'])

    print(params)

    con = sqlite3.connect(filename)
    cur = con.cursor()
    pre_query = get_select(args) + ' ' + 'FROM calls' + ' ' + 'JOIN referees AS r1 JOIN referees AS r2 JOIN referees AS r3' + ' ' + 'ON calls.game_code = r1.game_code AND calls.game_code = r2.game_code AND calls.game_code = r3.game_code' + ' ' + get_where(args)

    query=pre_query + ' GROUP BY calls.game_code, offending_team, defending_team, disadvantaged_player, committing_player;'
    print(query)
    query_result = cur.execute(query, params)
    query_result_list = query_result.fetchall()
    heads=get_header(cur)
    #print(heads)
    print('params')
    print(params)
    ratio_list = get_ratios(pre_query, params, con, cur)
    #print(pre_query)

    return (ratio_list, (heads, query_result_list))

def get_select(args):
    '''
    Generate the 'SELECT' portion of the query
    '''
    query='SELECT DISTINCT'
    to_add = ['game_name', 'r1.game_code', 'r1.referee_name', 'r2.referee_name', 'r3.referee_name', 'home_team', 'away_team', 'time', 'period', 'call_type', 'committing_player', 'offending_team', 'disadvantaged_player', 'defending_team', 'call_accuracy', 'comment'] 
    to_remove = []

    if 'refs1' in args.keys():
        to_remove.append('r1.referee_name')
        to_remove.append('r2.referee_name')
        to_remove.append('r3.referee_name')
    if 'committing_player' in args.keys():
        to_remove.append('committing_player')
    if 'offending_team' in args.keys():
        to_remove.append('offending_team')
    if 'disadvantaged_player' in args.keys():
        to_remove.append('disadvantaged_player')
    if 'defending_team' in args.keys():
        to_remove.append('defending_team')
    if 'call_type' in args.keys():
        to_remove.append('call_type')
    if 'call_accuracy' in args.keys():
        to_remove.append('call_accuracy')
    if 'home_team' in args.keys():
        to_remove.append('home_team')
    if 'away_team' in args.keys():
        to_remove.append('away_team')
    if 'comment' not in args.keys():
        to_remove.append('comment')
    
    final_adds = list(filter(lambda x: not(x in to_remove), to_add))

    for i in range(0, len(final_adds)-1):
        query += ' ' + final_adds[i] + ',' 
    query += ' ' + final_adds[-1] 

    return query

def get_where(args):
    '''
    Generate there 'WHERE' portion of the SQL query
    '''
    query = 'WHERE r1.referee_name != r2.referee_name AND r1.referee_name != r3.referee_name AND r2.referee_name != r3.referee_name'
    to_add=[]

    if 'refs1' in args.keys():
        to_add.append('r1.referee_name = ?')
        if args['refs2'] != '':
            to_add.append('r2.referee_name = ?')
            if args['refs3'] != '':
                to_add.append('r3.referee_name = ?')
    if 'committing_player' in args.keys():
        to_add.append('committing_player = ?')
    if 'offending_team' in args.keys():
        to_add.append('offending_team = ?')
    if 'disadvantaged_player' in args.keys():
        to_add.append('disadvantaged_player = ?')
    if 'defending_team' in args.keys():
        to_add.append('defending_team = ?')
    if 'call_type' in args.keys():
        to_add.append('call_type = ?')
    if 'call_accuracy' in args.keys():
        to_add.append('call_accuracy = ?')
    if 'home_team' in args.keys():
        to_add.append('home_team = ?')
    if 'away_team' in args.keys():
        to_add.append('away_team = ?')

    for i in range(0, len(to_add)):
        query += ' AND ' + to_add[i] 

    #query = query + ''
    #print(query)
    return query

def get_ratios(query, parameters, connection, cursor):
    '''
    Generate SQL query to return a list containing IC / (CC + IC), INC / (CNC + INC), 
    (INC + CNC) / total calls
    '''
    ratio_list = [0,0,0]
    call_list = ['IC', 'INC', 'CC', 'CNC']
    count_list = []
    new_query = 'SELECT DISTINCT COUNT(*) FROM(' + query + 'AND call_accuracy = ?);'
    #print(parameters)
    for call in call_list:
        parameters.append(call)
        a = cursor.execute(new_query, parameters) 
        list_tuple = a.fetchall()
        count_list.append(list_tuple[0][0])
        parameters.remove(call)
    #for call in call_list:
    e = cursor.execute('SELECT COUNT(*) FROM(' + query + ');', parameters)
    e1 = e.fetchall()
    total = e1[0][0]
    print('count list')
    print(count_list)
    if count_list[2]+count_list[0] != 0:
        ratio_list[0] = count_list[0]/(count_list[2]+count_list[0])
    if count_list[3]+count_list[1] != 0:
        ratio_list[1] = count_list[1]/(count_list[3]+count_list[1])
    if total != 0:
        ratio_list[2] = (count_list[0]+count_list[1])/total

    return ratio_list

def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i in range(len(s)):
        if s[i] == ".":
            s = s[i+1:]
            break
    return s