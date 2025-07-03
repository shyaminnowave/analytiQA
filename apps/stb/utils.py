import logging
from github import Github
from github.GithubException import BadCredentialsException, GithubException


logging = logging.getLogger(__name__)

def get_branch(auth: str, repo: str):
    try:
        g = Github(login_or_token=auth)
        repo = g.get_repo(repo)
        branches = repo.get_branches()
        return [branch.name for branch in branches]
    except BadCredentialsException as err:
        logging.error(str(err))
        return None
    except GithubException as e:
        logging.error(str(e))
        return None
    except Exception as e:
        logging.error(str(e))
        return None
