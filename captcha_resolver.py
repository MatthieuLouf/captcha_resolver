from io import BytesIO
import lxml.html
import urllib.request as urllib2
import pprint
import http.cookiejar as cookielib
from PIL import Image
import base64
import pytesseract
import requests

URL_CAPTCHA = 'http://challenge01.root-me.org/programmation/ch8/'

def load_captcha(html):
    tree = lxml.html.fromstring(html)
    img_data = tree.cssselect('img')[0].get('src')
    img_data = img_data.partition(',')[-1]
    base64_bytes = img_data.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    file_like = BytesIO(sample_string_bytes)
    img = Image.open(file_like)
    return img

ckj = cookielib.CookieJar()
browser = urllib2.build_opener(urllib2.HTTPCookieProcessor(ckj))
not_success= True

web_page =browser.open(URL_CAPTCHA)
html = web_page.read()
cookie = web_page.headers['Set-Cookie'].partition('=')[2].partition(';')[0]

count = 0
while(count<100 and not_success):
    count+=1
    print(count)

    img = load_captcha(html)
    img.save('captcha_original.png')
    gray = img.convert('L')
    gray.save('captcha_gray.png')
    bw = gray.point(lambda x: 255 if (x > 220 or x <1) else 0, '1')
    bw.save('captcha_thresholded.png')

    result=pytesseract.image_to_string(bw)

    print(result)
    data = {"cametu":result}
    proxies = {
     "http": "http://127.0.0.1:8080",
     "https": "http://127.0.0.1:8080",
    }

    x = requests.post(URL_CAPTCHA, data = data,headers ={"Cookie": "PHPSESSID="+cookie})

    if("Try again" in x.text ==False):
        not_success = False
        print(x.text)
    html=x.text
