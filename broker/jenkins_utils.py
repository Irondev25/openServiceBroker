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

# def get_job(server, job_name):
#     try:
#         return serv


def get_git_values(github_url):
    """
    return dictionary
    {
        'author':author,
        "repo_name":repo_name
    }
    """
    values = github_url.split('/')
    author = values[3]
    repo_name = values[4].split('.')[0]
    return {
        'author':author,
        "repo_name":repo_name
    }

def create_webhook(github_repo,jenkins_url, git_values):
    API_URL = 'https://api.github.com/repos/'+git_values['author']+'/'+git_values['repo_name']+'/hooks'
    print(API_URL)
    PARAMS = {
        "name":"webhook",
        "active": True,
        "events": ["push","merge"],
        "config": {
            "url": jenkins_url+'github-webhook/',
            "content_type" : "json",
            "insecure_ssl" : "0"
        }
    }
    r = requests.post(url=API_URL,data=json.dumps(PARAMS))
    if r.status_code == 201:
        print("Webhook Created")
        logger.info("Webhook Created")
    else:
        raise Exception("Falied To Create Webhook: %d", r.status_code)


def provision_job(github_repo_url):
    github_uri = github_repo_url
    git_values = get_git_values(github_repo_url)
    job_name = git_values['author']+":"+git_values['repo_name']
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
        create_webhook(github_repo,jenkins_url, git_values)
    except Exception as e:
        jobs = server.get_jobs()
        server.delete_job(job_name)
        raise e
