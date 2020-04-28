import os
import jenkins
import json
import time
import requests
import logging
import json

from jenkins import JenkinsException
from broker import github_utils as gh_utils

JENKINS_ID=os.getenv('JENKINS_USERID')
JENKINS_PASSWD=os.getenv('JENKINS_PASSWORD')
JENKINS_URL=os.getenv('JENKINS_URL')

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
  <publishers>
    <hudson.plugins.emailext.ExtendedEmailPublisher plugin="email-ext@2.69">
      <recipientList>%s</recipientList>
      <configuredTriggers>
        <hudson.plugins.emailext.plugins.trigger.FailureTrigger>
          <email>
            <subject>$PROJECT_DEFAULT_SUBJECT</subject>
            <body>$PROJECT_DEFAULT_CONTENT</body>
            <recipientProviders>
              <hudson.plugins.emailext.plugins.recipients.DevelopersRecipientProvider/>
              <hudson.plugins.emailext.plugins.recipients.ListRecipientProvider/>
            </recipientProviders>
            <attachmentsPattern></attachmentsPattern>
            <attachBuildLog>false</attachBuildLog>
            <compressBuildLog>false</compressBuildLog>
            <replyTo>$PROJECT_DEFAULT_REPLYTO</replyTo>
            <contentType>project</contentType>
          </email>
        </hudson.plugins.emailext.plugins.trigger.FailureTrigger>
        <hudson.plugins.emailext.plugins.trigger.SuccessTrigger>
          <email>
            <subject>$PROJECT_DEFAULT_SUBJECT</subject>
            <body>$PROJECT_DEFAULT_CONTENT</body>
            <recipientProviders>
              <hudson.plugins.emailext.plugins.recipients.DevelopersRecipientProvider/>
              <hudson.plugins.emailext.plugins.recipients.ListRecipientProvider/>
            </recipientProviders>
            <attachmentsPattern></attachmentsPattern>
            <attachBuildLog>false</attachBuildLog>
            <compressBuildLog>false</compressBuildLog>
            <replyTo>$PROJECT_DEFAULT_REPLYTO</replyTo>
            <contentType>project</contentType>
          </email>
        </hudson.plugins.emailext.plugins.trigger.SuccessTrigger>
      </configuredTriggers>
      <contentType>both</contentType>
      <defaultSubject>$DEFAULT_SUBJECT</defaultSubject>
      <defaultContent>$DEFAULT_CONTENT</defaultContent>
      <attachmentsPattern></attachmentsPattern>
      <presendScript>$DEFAULT_PRESEND_SCRIPT</presendScript>
      <postsendScript>$DEFAULT_POSTSEND_SCRIPT</postsendScript>
      <attachBuildLog>true</attachBuildLog>
      <compressBuildLog>false</compressBuildLog>
      <replyTo>rahulbhaskar.is17@bmsce.ac.in</replyTo>
      <from></from>
      <saveOutput>false</saveOutput>
      <disabled>false</disabled>
    </hudson.plugins.emailext.ExtendedEmailPublisher>
  </publishers>
  <buildWrappers/>
</project>"""


def get_jenkins_server(url, username, password):
    try:
        return jenkins.Jenkins(url, username=username, password=password)
    except Exception as e:
        print("Unable to connect to Jenkins Server")
        raise e


def create_job(server, job_name, description, github_url, github_repo, email):
    XML_CONFIG = XML_TEMPLATE % (description, github_url, github_repo, email)
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


# def get_git_values(github_url):
#     """
#     return dictionary
#     {
#         "author":author,
#         "repo_name":repo_name
#     }
#     """
#     values = github_url.split('/')
#     author = values[3]
#     repo_name = values[4].split('.')[0]
#     return {
#         "author": author,
#         "repo_name": repo_name
#     }


# def create_webhook(github_repo, jenkins_url, git_values, id, password):
#     API_URL = 'https://api.github.com/repos/' + \
#         git_values['author']+'/'+git_values['repo_name']+'/hooks'
#     print(API_URL)
#     payload = {
#         "name": "web",
#         "active": True,
#         "events": ["push"],
#         "config": {
#             "url": jenkins_url+'github-webhook/',
#             "content_type": "json",
#             "insecure_ssl": "0"
#         }
#     }
#     headers = {
#         'Authorization': 'Basic SXJvbmRldjI1OlJhaHVsYmhhc2thcjEyMw==',
#         'Content-Type': 'text/plain'
#     }
#     response = requests.request("POST", API_URL, headers=headers, data=json.dumps(payload))
#     if response.status_code == 201:
#         print("Webhook Created")
#         logger.info("Webhook Created")
#     else:
#         raise Exception("Falied To Create Webhook: %d", response.status_code)
#     return {
#       'hook_id': response.json()['id'],
#       'API_URL': API_URL
#     }






def provision_job(project_name, github_id, github_pass, email):
    # github_uri = github_repo_url
    # git_values = get_git_values(github_repo_url)
    # job_name = git_values['author']+"_"+git_values['repo_name']
    # description = github_uri
    # github_url = github_uri[:-4] + '/'
    # github_repo = github_uri
    # username = "admin"
    # password = "admin"
    # jenkins_url = "localhost:8080"

    try:
        server = get_jenkins_server(JENKINS_URL, JENKINS_ID, JENKINS_PASSWD)
    except Exception as e:
        raise e

    try:
      repo_details = gh_utils.create_githubrepo(github_id,github_pass,project_name)
    except Exception as e:
      raise e
    
    try:
        create_job(server, project_name, "OBS enabled repository", repo_details.get('html_url'), repo_details.get('clone_url'),email)
    except Exception as e:
      gh_utils.delete_repo(github_id,github_pass,project_name)
      raise e
    # repo_details = {
    #     'html_url' : "repo.html_url",
    #     'clone_url': "repo.clone_url",
    #     'hooks_url': "repo.hooks_url",
    #     'hook_id'  : "hook.id"
    # }
    return repo_details
    


def deprovision_job(project_name, api_url, hook_id):
  try:
    server = get_jenkins_server(JENKINS_URL, JENKINS_ID, JENKINS_PASSWD)
  except Exception as e:
    raise e
  gh_utils.delete_webhook(api_url,hook_id)
  delete_job(server,project_name)
