#coding=utf-8
import base64, json, pycurl

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

'''
class Pycurl():
    def __init__(self):
        self.curl = pycurl.Curl()
        self.buffer = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, self.buffer.write)
'''
#def init_pycurl(self,)

def http_request(url, username, password, proto='http', params=None):
    curl = pycurl.Curl()
    buffer = StringIO()
    curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    curl.setopt(pycurl.URL, url)
    if proto == "https":
        #不检查证书
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)
    #python 2.x
    #authorization = 'Basic %s'%(('%s:%s'%(username, password)).encode('base64').replace('\n', ''))
    #python 3.x 中字符都为 Unicode 编码，而 b64encode 函数参数为 byte 类型，所以必须先转码，而函数返回的结果也为 byte 类型，所以需要使用 str() 函数把结果转码
    authorization = 'Basic %s'%str(base64.b64encode(('%s:%s'%(username, password)).encode('utf-8')), 'utf-8').replace('\n', '')

    curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json', 'Authorization:%s' % authorization])
    if params:
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.POSTFIELDS, params)
    try:
        curl.perform()
        status = curl.getinfo(pycurl.RESPONSE_CODE)
        data = {
            "status" : status,
            "body" : buffer.getvalue(),
        }
    except Exception as e:
        raise NameError(str(e))
    finally:
        curl.close()
    return data

def down_file(url, filename, username=None, password=None):
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    if username and password:
        curl.setopt(pycurl.USERNAME, username)
        curl.setopt(pycurl.PASSWORD, password)
    with open(filename, 'wb') as f:
        curl.setopt(pycurl.WRITEFUNCTION, f.write)
        try:
            curl.perform()
        except Exception as e:
            raise NameError(str(e))
        finally:
            curl.close()

def upload_file(url, filepath, username=None, password=None):
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.UPLOAD, 1)
    if username and password:
        curl.setopt(pycurl.USERNAME, username)
        curl.setopt(pycurl.PASSWORD, password)

    with open(filepath, 'rb') as f:
        curl.setopt(pycurl.READFUNCTION, f.read)
        try:
            curl.perform()
        except Exception as e:
            raise NameError(str(e))
        finally:
            curl.close()
    


if __name__ == '__main__':
    '''
    # http_request test
    url1 = 'https://10.8.11.35:9997/rest/ag/global/system/SystemInfo/version'
    url2 = 'https://10.8.11.35:9997/rest/ag/global/cli_extend'
    #pc = Pycurl()
    #pc = Pycurl()
    params = json.dumps({'cmd':'show restapi'})
    result = http_request(url2, 'array', 'admin', 'https', params)
    print(result)
    result = http_request(url1, 'array', 'admin', 'https')
    print(result)
    '''
    #down_file test
    #down_file('http://10.3.0.20/sp2/build/CA-SNMP-MIB-Rel_AG_9_4_0_210.txt', 'mib.txt')
    #down_file('ftp://10.3.0.40/liyi/all.diff', 'all.diff', 'arraytmp', 'arraytmp')
    upload_file('ftp://10.3.0.40/liyi/95_restful/heiheihei.diff', 'heiheihei.diff', 'arraytmp', 'arraytmp')

