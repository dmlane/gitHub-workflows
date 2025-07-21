#!/usr/bin/env python3
import os
import argparse
from datetime import datetime, timedelta
from github import Github

parser = argparse.ArgumentParser()
parser.add_argument('--days', type=int, default=90)
parser.add_argument('--keep', type=int, default=5)
args = parser.parse_args()

token = os.environ["GITHUB_TOKEN"]
repo_name = os.environ["GITHUB_REPOSITORY"]

g = Github(token)
repo = g.get_repo(repo_name)
releases = list(repo.get_releases())

# Sort releases by creation date (newest first)
releases.sort(key=lambda r: r.created_at, reverse=True)

cutoff = datetime.utcnow() - timedelta(days=args.days)
to_delete = []

for idx, release in enumerate(releases):
    if idx < args.keep:
        continue  # Always keep the N most recent
    if release.created_at >= cutoff:
        continue  # Keep recent ones
    to_delete.append(release)

print(f"Found {len(to_delete)} releases to delete.")
for release in to_delete:
    print(f"Deleting release: {release.title} ({release.tag_name})")
    release.delete_release()
    try:
        ref = repo.get_git_ref(f"tags/{release.tag_name}")
        ref.delete()
        print(f"Deleted tag: {release.tag_name}")
    except Exception as e:
        print(f"Tag not found or already deleted: {release.tag_name}")

