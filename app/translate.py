import json,random,hashlib,http.client
from flask_babel import _
from app import app
from urllib import parse

def translate(q, fromLang, toLang):
    if 'APPID' not in app.config or not app.config['APPID']:
        return _('Error:the translation service is not configured.')
    if 'BD_TRANSLATOR_KEY' not in app.config or not app.config['BD_TRANSLATOR_KEY']:
        return _('Error:the translation service is not configured.')
    appid = app.config['APPID']
    secretKey = app.config['BD_TRANSLATOR_KEY']

    httpClient = None
    myurl = '/api/trans/vip/translate'
    salt = random.randint(32768, 65536)

    sign = appid+q+str(salt)+secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode(encoding='utf-8'))
    sign = m1.hexdigest()
    myurl = myurl+'?appid='+appid+'&q='+parse.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        response = httpClient.getresponse()#response是HTTPResponse对象
        r = response.read().decode('utf-8')
        d = json.loads(r)

        l = d['trans_result']
        l1 = l[0]['dst']

        return(l1)
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()