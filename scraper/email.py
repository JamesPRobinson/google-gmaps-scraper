from bs4 import UnicodeDammit
from fake_useragent import UserAgent
import re
import requests
from requests_html import HTML
import traceback
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
JUNK_EMAIL_TERMS = ['/', '@example', 'johndoe','.png', 'wixpress', '@email.com', '.jpg', '@sentry']


def check_url(url):
    if not re.match('(?:http|ftp|https)://', url):
        return 'http://{}'.format(url)
    return url


def deep_extract_email(html):
    email = ''
    ua = UserAgent()
    headers = {'User-Agent': str(ua.random)}
    for link in html.absolute_links:
        if any(e for e in ['contac','konta', 'contat'] if e in link.lower()):
            if 'mailto' in link:
                return link.replace('mailto', '')
            url = check_url(link)
            try:
                response = requests.get(url, verify=False, headers=headers, timeout=(5,5))    
                if response.ok:  
                    html = HTML(html=response.text)
                    email = extract_email(html)
            except Exception as e:
                print(e)
                traceback.print_exc()
                break
    return email
    

def extract_email(html):
    try:
        encoding = UnicodeDammit(html.raw_html).original_encoding 
        encoding = encoding if encoding else 'utf-8'
        for email_match in re.finditer(EMAIL_REGEX, html.raw_html.decode(encoding), re.IGNORECASE):
            if 'mailto' in email_match.group():
                return email_match.group().replace('mailto', '')
            if is_valid_email(email_match.group()):
                return email_match.group()    
    except Exception as e:
        print(e)
        traceback.print_exc()
    return ''
    

def get_email(url):
    url = check_url(url)
    email = ''
    ua = UserAgent()
    headers = {'User-Agent': str(ua.random)}
    try:
        response = requests.get(url, verify=False, headers=headers, stream=True, timeout=(5,5))
        if response.ok: 
            try:
                content_length = int(response.headers['content-length'])
            except:
                content_length = 0
            if int(content_length) < 10*1024*1024: # 10 Mb
                html = HTML(html=response.content)
                email = extract_email(html)
                if not email:
                    email = deep_extract_email(html) 
    except Exception as e:
        print(e)
        traceback.print_exc()
    return email


# Necessary step while I figure out how to modify the regex to accomodate for this
# e.g. avoid
# //www.google.fr/maps/place/Centre+Dentaire+LABELIA+Quai+de+Sa%C3%B4ne/@45.788322
# //cdn.jsdelivr.net/gh/fancyapps/fancybox@3.5.7
# //www.soula-philippe-antenne.fr/wp-content/uploads/2019/08/logo_dark@2x-1.png
def is_valid_email(email):
    return not any([e for e in JUNK_EMAIL_TERMS if e in email]) and any([e.isalpha() for e in email.split('@')[1]]) if email else ''

