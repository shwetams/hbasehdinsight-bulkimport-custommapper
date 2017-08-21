import sys
import json
rowkey_prefix = '<if you have a particular prefix>'
row_key_col = '<column name from the headers file whose values will be used for row keys>'
row_key = ''
try:
    with open('headers.json') as headervals:
        headers = json.load(headervals)
    with open('colkeys.json') as colkeysvals:
        colkeys = json.load(colkeysvals)
    for line in sys.stdin:
        line = line.strip()
        vals = line.split('|')
        if len(vals)==15:

            i = 0
            col_identifier = ''
            isFirstCol = True
            line = "{"
            for v in vals:
                if headers[i] == row_key_col:
                    row_key = member_id + "_" + v.encode('utf-8').replace('{','(').replace('}','')
                if i == 0:
                    line = line + '"' + headers[i] + '":"' + v.encode('utf-8').replace('{','(').replace('}','') + '"'
                else:
                    line = line + "," + '"' + headers[i] + '":"' + v.encode('utf-8').replace('{','(').replace('}','') + '"'
                for c in colkeys:
                    if headers[i].strip() == c:
                        if isFirstCol == False:
                            col_identifier = col_identifier + "_" + v.encode('utf-8').replace('{','(').replace('}','')
                        else:
                            col_identifier = v.encode('utf-8').replace('{','(').replace('}','')
                            isFirstCol = False

                i = i + 1
            line = line + "}"
            line = row_key + '|' + col_identifier + "|" + line
        print(line)
except Exception as e:
    pass