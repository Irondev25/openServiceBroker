import jenkins
import json
import time
import requests
import logging
import json

from jenkins import JenkinsException

logger = logging.getLogger(__name__)

XML_TEMPLATE = """<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>%s</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <com.coravy.hudson.plugins.github.GithubProjectProperty plugin="github@1.29.5">
      <projectUrl>%s</projectUrl>
      <displayName></displayName>
    </com.coravy.hudson.plugins.github.GithubProjectProperty>
  </properties>
  <scm class="hudson.plugins.git.GitSCM" plugin="git@4.2.2">
    <configVersion>2</configVersion>
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <url>%s</url>
      </hudson.plugins.git.UserRemoteConfig>
    </userRemoteConfigs>
    <branches>
      <hudson.plugins.git.BranchSpec>
        <name>*/master</name>
      </hudson.plugins.git.BranchSpec>
    </branches>
    <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
    <submoduleCfg class="list"/>
    <extensions/>
  </scm>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>
    <com.cloudbees.jenkins.GitHubPushTrigger plugin="github@1.29.5">
      <spec></spec>
    </com.cloudbees.jenkins.GitHubPushTrigger>
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>echo &quot;sucess &quot;
ls -la</command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers/>
</project>"""
JENKINS_URL = "http://34.107.140.118/"
JENKINS_ID = "admin"
JENKINS_PASSWD = "admin"


def get_jenkins_server(url, username, password):
    try:
        return jenkins.Jenkins(url, username=username, password=password)
    except Exception as e:
        print("Unable to connect to Jenkins Server")
        raise e


def create_job(server, job_name, description, github_url, github_repo):
    XML_CONFIG = XML_TEMPLATE % (description, github_url, github_repo)
    try:
        return server.create_job(job_name, XML_CONFIG)
    except JenkinsException as e:
        print("Unable to create Jenkins Job")
        raise e
    
def delete_job(server, job_name):
  server.delete_job(job_name)

# def get_job(server, job_name):
#     try:
#         return serv


def get_git_values(github_url):
    """
    return dictionary
    {
        "author":author,
        "repo_name":repo_name
    }
    """
    values = github_url.split('/')
    author = values[3]
    repo_name = values[4].split('.')[0]
    return {
        "author": author,
        "repo_name": repo_name
    }


def create_webhook(github_repo, jenkins_url, git_values, id, password):
    API_URL = 'https://api.github.com/repos/' + \
        git_values['author']+'/'+git_values['repo_name']+'/hooks'
    print(API_URL)
    payload = {
        "name": "web",
        "active": True,
        "events": ["push"],
        "config": {
            "url": jenkins_url+'github-webhook/',
            "content_type": "json",
            "insecure_ssl": "0"
        }
    }
    headers = {
        'Authorization': 'Basic SXJvbmRldjI1OlJhaHVsYmhhc2thcjEyMw==',
        'Content-Type': 'text/plain'
    }
    response = requests.request("POST", API_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 201:
        print("Webhook Created")
        logger.info("Webhook Created")
    else:
        raise Exception("Falied To Create Webhook: %d", response.status_code)
    return {
      'hook_id': response.json()['id'],
      'API_URL': API_URL
    }

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



def provision_job(github_repo_url, github_id, github_pass):
    github_uri = github_repo_url
    git_values = get_git_values(github_repo_url)
    job_name = git_values['author']+"_"+git_values['repo_name']
    description = github_uri
    github_url = github_uri[:-4] + '/'
    github_repo = github_uri
    username = "admin"
    password = "admin"
    jenkins_url = "http://34.107.140.118/"

    try:
        server = get_jenkins_server(jenkins_url, username, password)
    except Exception as e:
        raise e
    try:
        create_job(server, job_name, description, github_url, github_repo)
    except Exception as e:
        raise e

    try:
        github_details = create_webhook(github_repo, jenkins_url, git_values, github_id, github_pass)
    except Exception as e:
        delete_job(server,job_name)
        raise e
    return {
        'job_name': job_name,
        'github_hook_id': github_details['hook_id'],
        'github_api_url': github_details['API_URL']
    }


def deprovision_job(job_name,github_hook_id,github_api_url):
  try:
    server = get_jenkins_server(JENKINS_URL, JENKINS_ID, JENKINS_PASSWD)
  except Exception as e:
    raise e
  delete_webhook(github_api_url,github_hook_id)
  delete_job(server,job_name)
