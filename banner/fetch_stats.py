#!/usr/bin/env python3

import collections
import json
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent

CONTRIBUTIONS_QUERY = (
    "query($login:String!){user(login:$login){contributionsCollection"
    "{contributionCalendar{totalContributions}}}}"
)


def run(args, cwd=None):
    return subprocess.run(
        args, capture_output=True, text=True, check=True, cwd=cwd
    ).stdout


def api(path, paginate=False):
    return json.loads(run(["gh", "api", path] + (["--paginate"] if paginate else [])))


def owner():
    from_env = os.environ.get("GITHUB_REPOSITORY_OWNER")
    if from_env:
        return from_env
    try:
        url = run(["git", "remote", "get-url", "origin"], cwd=HERE).strip()
        match = re.search(r"[:/]([^/:]+)/[^/]+?(?:\.git)?$", url)
        if match:
            return match.group(1)
    except subprocess.CalledProcessError:
        pass
    return api("/user")["login"]


def contributions(login):
    return int(
        run([
            "gh", "api", "graphql",
            "-f", f"query={CONTRIBUTIONS_QUERY}",
            "-f", f"login={login}",
            "--jq", ".data.user.contributionsCollection"
                    ".contributionCalendar.totalContributions",
        ]).strip()
    )


def collect():
    login = owner()
    profile = api(f"/users/{login}")
    repos = [
        repo for repo in api(f"/users/{login}/repos?per_page=100", paginate=True)
        if not repo["fork"]
    ]

    languages = collections.Counter()
    for repo in repos:
        languages.update(api(f"/repos/{login}/{repo['name']}/languages"))

    return {
        "login": login,
        "name": profile.get("name") or login,
        "tagline": (profile.get("bio") or "").strip(),
        "repos": len(repos),
        "stars": sum(repo["stargazers_count"] for repo in repos),
        "followers": profile.get("followers", 0),
        "contributions": contributions(login),
        "languages": dict(languages.most_common()),
    }


def main(path):
    stats = collect()
    pathlib.Path(path).write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"{path}: {stats['login']} — {stats['repos']} repo, "
        f"{len(stats['languages'])} jezykow, {stats['stars']} gwiazdek, "
        f"{stats['contributions']} kontrybucji, "
        f"{sum(stats['languages'].values()) / 1e6:.2f} MB"
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "stats.json")
