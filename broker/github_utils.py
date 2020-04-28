from github import Github
import requests
import os

WEBHOOK_URL = os.getenv('WEBHOOK_URL')

def create_githubrepo(userid,userpass,project_name):
    githubObj = Github(userid,userpass)
    #create repo
    try:
      repo = githubObj.get_user().create_repo(project_name)
    except Exception as e:
      raise e

    #create webhook
    EVENTS = ["push","pull_request"]
    config = {
        "url": WEBHOOK_URL,
        "content_type": "json",
        "insecure_ssl" : "0"
    }
    try:
      hook = repo.create_hook("web",config,EVENTS,active=True)  
    except Exception as e:
      repo.delete()
      raise e
      
    repo_details = {
        'html_url' : repo.html_url,
        'clone_url': repo.clone_url,
        'hooks_url': repo.hooks_url,
        'hook_id'  : hook.id
    }
    return repo_details

def delete_repo(userid,userpass,project_name):
  githubObj = Github(userid,userpass)
  githubObj.get_user().get_repo(project_name).delete()


def delete_webhook(API_URL, id):
  url = API_URL + '/' + str(id)
  payload = {}
  headers = {
      'Authorization': 'Basic SXJvbmRldjI1OlJhaHVsYmhhc2thcjEyMw=='
  }
  response = requests.request("DELETE",url,headers=headers,data=payload)
  if(response.status_code == 204):
    print("Webhook Sucessfully Deleted")
  else:
    raise Exception("Failed to delete Webhook: %d", response.status_code)
