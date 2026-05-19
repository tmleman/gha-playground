#!/usr/bin/env python3
"""
Simplified assignment script for PWN Request POC.
Demonstrates that attacker-controlled YAML is parsed in a context with secrets.
"""

import argparse
import os
import sys

import yaml


def main():
    parser = argparse.ArgumentParser(description="POC assignment script")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-o", "--org", required=True)
    parser.add_argument("-r", "--repo", required=True)
    parser.add_argument("-M", "--maintainer-file", default="MAINTAINERS.yml")
    parser.add_argument("-P", "--pull-request", type=int)
    parser.add_argument("-I", "--issue", type=int)
    parser.add_argument("--updated-maintainer-file", default=None)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    token_preview = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "(empty)"

    print(f"[POC] Organization: {args.org}")
    print(f"[POC] Repository: {args.repo}")
    print(f"[POC] Token present: {'YES' if token else 'NO'} (preview: {token_preview})")
    print(f"[POC] Maintainer file: {args.maintainer_file}")

    # Load base MAINTAINERS.yml
    with open(args.maintainer_file) as f:
        base_data = yaml.safe_load(f)
    print(f"[POC] Base maintainer areas: {list(base_data.keys())}")

    # Load attacker-controlled file if provided
    if args.updated_maintainer_file:
        print(f"\n[POC] ⚠️  Loading ATTACKER-CONTROLLED file: {args.updated_maintainer_file}")
        with open(args.updated_maintainer_file) as f:
            pr_data = yaml.safe_load(f)
        print(f"[POC] PR maintainer areas: {list(pr_data.keys())}")

        # Show what changed (simulates compare_areas)
        base_areas = set(base_data.keys())
        pr_areas = set(pr_data.keys())
        added = pr_areas - base_areas
        removed = base_areas - pr_areas

        if added:
            print(f"[POC] ⚠️  NEW areas added by PR: {added}")
            for area in added:
                entry = pr_data[area]
                maintainers = entry.get("maintainers", [])
                print(f"[POC]   Area '{area}' maintainers: {maintainers}")
                print(f"[POC]   ⚠️  These usernames will be looked up via GitHub API using the secret token!")

        if removed:
            print(f"[POC] Areas removed by PR: {removed}")

    # Demonstrate that the token is accessible in this context
    if token:
        print(f"\n[POC] 🔴 CRITICAL: Secret token is available in this execution context!")
        print(f"[POC] 🔴 An attacker controlling the YAML input could exfiltrate this token")
        print(f"[POC] 🔴 Token length: {len(token)} characters")

    print("\n[POC] Script completed successfully")


if __name__ == "__main__":
    main()
