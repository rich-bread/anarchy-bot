import json, requests

url = 'https://script.google.com/macros/s/AKfycbx0lIMbkYa9Mq9Ga78oLXnePkt1q-td74MYJpGBGaqw4pxwdAtzpltaBT_Ut2jinKXRUg/exec?'

#DBへのPOST処理
async def post_db(data, param, item):
    uurl = url + f'param={param}' + '&' + f'item={item}'
    output = requests.post(uurl, data=json.dumps(data))
    return output

#同チームメンバーかどうかを確認するGET処理
async def verify_team(param, authorId, subjectId):
    payload = {'param': param, 'authorId': authorId, 'subjectId': subjectId}
    output = requests.get(url, params=payload)
    return output

#いずれかのチームのリーダーかを確認するGET処理
async def verify_leader(param, authorID):
    payload = {'param': param, 'authorID': authorID}
    output = requests.get(url, params=payload)
    return output

async def get_db(param, table, subjectID, item):
    payload = {'param': param, 'subjectID': subjectID, 'table': table, 'item': item}
    output = requests.get(url, params=payload)
    return output

async def check_indiv(subjectID):
    payload = {'param': 'check-indiv', 'subjectID': subjectID}
    output = requests.get(url, params=payload)
    return output