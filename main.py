from cut_pic import cut
from config import config
from api import github_api

if __name__ == "__main__":
    h, w = cut()
    github = github_api(config['user_name'], config['passwd'])
    github.login()
    org_list = []
    for i in github.organizations_list():
        if i['login'].find(f'{config["user_name"]}-pic-matrix') == 0:
            org_list.append(i['login'])
    for y in range(0, h):
        for x in range(0, w):
            org_name = f'{config["user_name"]}-pic-matrix-{y}-{x}'
            sub_img_path = f'./out/{y}-{x}.png'
            print(f'\n{y}-{x}/{h-1}-{w-1}: {org_name}')
            if org_name in org_list:
                github.organizations_edit_avatar(org_name, sub_img_path)
                org_list.remove(org_name)
            else:
                github.organizations_new(org_name)
                github.organizations_turn_to_public(org_name)
                github.organizations_edit_avatar(org_name, sub_img_path)
    for org_name in org_list:
        github.organizations_del(org_name)
