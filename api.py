import requests
import os
from lxml import etree

proxy = {
    'http': 'socks5://127.0.0.1:1902',
    'https': 'socks5://127.0.0.1:1902'
}

class github_api:
    def __init__(self, user_name, passwd):
        self.headers = {
            'Referer': 'https://github.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        self.session = requests.Session()
        self.user_name = user_name
        self.passwd = passwd

    def login(self):
        print("start login: " + self.user_name)
        # get token
        response = self.session.get('https://github.com/login', headers = self.headers, proxies = proxy)
        selector = etree.HTML(response.text)
        token = selector.xpath('//div//input[2]/@value')[0]
        print("____get token: " + token)
        post_data = {
            'commit': 'Sign in',
            'utf8': '✓',
            'authenticity_token': token,
            'login': self.user_name,
            'password': self.passwd
        }
        self.session.post('https://github.com/session', data = post_data, headers = self.headers, proxies = proxy)
        print('____login complish')
        
    def organizations_new(self, name, email="none@none.com"):
        print('start new organization: ' + name)
        response = self.session.get('https://github.com/account/organizations/new?coupon=&plan=team_free', headers = self.headers, proxies = proxy)
        selector = etree.HTML(response.text)
        token = selector.xpath('//form[@id="org-new-form"]//input[@name="authenticity_token"]/@value')[0]
        print("____get token: " + token)
        post_data = {
            'utf8': '✓',
            'authenticity_token': token,
            'coupon': '',
            'organization[plan]': 'free',
            'organization[login]': name,
            'organization[billing_email]': email,
            'terms_of_service_type': 'standard',
            'organization[company_name]': ''
        }
        self.session.post('https://github.com/organizations', data = post_data, headers = self.headers, proxies = proxy)
        print(f'____new organization {name} complish')

    def organizations_del(self, name):
        print('start delete organization: ' + name)
        response = self.session.get(f'https://github.com/organizations/{name}/settings/profile?_pjax=%23js-pjax-container', headers = self.headers, proxies = proxy)
        selector = etree.HTML(response.text)
        token = selector.xpath('//form[@id="cancel_plan"]//input[@name="authenticity_token"]//@value')[0]
        danger_zone_token = selector.xpath('//input[@name="dangerzone"]/@value')[0]
        print("____get token: " + token)
        post_data = {
            'utf8': '✓',
            'authenticity_token': token,
            '_method': 'delete',
            'dangerzone': danger_zone_token
        }
        self.session.post(f'https://github.com/organizations/{name}', data = post_data, headers = self.headers, proxies = proxy)
        print(f'____delete organization {name} complish')

    def organizations_edit_avatar(self, name, path):
        print('start upload new avatar ' + path + ' for organization: ' + name)
        response = self.session.get(f'https://github.com/organizations/{name}/settings/profile', headers = self.headers, proxies = proxy)
        selector = etree.HTML(response.text)
        token = selector.xpath('//file-attachment/@data-upload-policy-authenticity-token')[0]
        org_id = selector.xpath('//form/@data-scope-id')[0]
        print("____get token: " + token)
        img_size = os.path.getsize(path)
        img_name = os.path.basename(path)
        img = open(path, 'rb')
        post_data = {
            'name': img_name,
            'size': img_size,
            'content_type': 'image/png' ,
            'authenticity_token': token,
            'organization_id': org_id,
            'owner_type': 'User',
            'owner_id': org_id
        }
        response = self.session.post('https://github.com/upload/policies/avatars', data = post_data, files = {'f': 'f'}, headers = self.headers, proxies = proxy)
        token = response.json()['upload_authenticity_token']
        remote_auth = response.json()['header']['GitHub-Remote-Auth']
        print("____get token2: " + token)
        print("____get remote auth: " + remote_auth)
        self.session.options('https://uploads.github.com/avatars', headers = self.headers, proxies = proxy)
        post_data = {
            "authenticity_token": token,
            "owner_type": "User",
            "owner_id": org_id,
            "size": img_size,
            "content_type": "image/png"
        }
        post_files = [
            ('file', img)
        ]
        headers = self.headers
        headers["GitHub-Remote-Auth"] = remote_auth
        response = self.session.post('https://uploads.github.com/avatars', data = post_data, headers = headers, files = post_files, proxies = proxy)
        upload_id = response.json()['id']
        img_width = response.json()['width']
        img_height = response.json()['height']
        print("____get avatar upload id: " + str(upload_id))
        print('____avatar upload url: ' + response.json()['url'])
        print('____width: ' + str(img_width))
        print('____height: ' + str(img_height))
        response = self.session.get(f'https://github.com/settings/avatars/{upload_id}', headers = self.headers, proxies = proxy)
        selector = etree.HTML(response.text)
        token = selector.xpath('//input[@name="authenticity_token"]/@value')[0]
        post_data = {
            'op': 'save',
            'utf8': '✓',
            'authenticity_token': token,
            'cropped_x': 0,
            'cropped_y': 0,
            'cropped_width': min(img_width, img_height),
            'cropped_height': min(img_width, img_height)
        }
        self.session.post(f'https://github.com/settings/avatars/{upload_id}', headers = self.headers, data = post_data, proxies = proxy)
        img.close()
        print("____edit finish")

    def organizations_turn_to_public(self, name):
        print(f"start to set organization {name} to public.")
        response = self.session.get(f'https://github.com/orgs/{name}/people', headers = self.headers, proxies = proxy)
        selector = etree.HTML(response.text)
        token = selector.xpath('//div[@class="select-menu-list"][1]/form/input[@name="authenticity_token"]/@value')[0]
        member_id = selector.xpath('//div[@class="select-menu-list"][1]/form/input[@name="member_ids"]/@value')[0]
        print("____get token: " + token)
        print("____get member id: " + member_id)
        post_data = {
            'publicize': 1,
            'utf8': '✓',
            '_method': 'put',
            'authenticity_token': token,
            'member_ids': member_id,
            'publicize': 1
        }
        self.session.post(f'https://github.com/orgs/{name}/people/set_visibility', headers = self.headers, data = post_data, proxies = proxy)
        print("____set finish");
   
    def organizations_list(self):
        return (self.session.get(f'https://api.github.com/users/{self.user_name}/orgs', headers = self.headers, proxies = proxy).json())



