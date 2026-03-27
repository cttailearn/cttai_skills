#!/usr/bin/env python3
"""
Import cookies from browser export to patchright state.json format
"""

import json
import sys
from pathlib import Path

def convert_cookies_to_state(cookies, output_path):
    """
    Convert cookies to patchright storage_state format

    Args:
        cookies: List of cookie dictionaries
        output_path: Path to save state.json
    """
    # Fix cookies - patchright requires sameSite to be "Strict", "Lax", "None", or undefined
    fixed_cookies = []
    for cookie in cookies:
        # Remove sameSite if it's null (invalid in patchright)
        if cookie.get("sameSite") is None or cookie.get("sameSite") == "no_restriction":
            # "no_restriction" is Firefox format, convert to "None" for Chromium
            if cookie.get("sameSite") == "no_restriction":
                cookie["sameSite"] = "None"
            else:
                # Remove null sameSite - Chromium treats null sameSite as not set
                cookie.pop("sameSite", None)
        fixed_cookies.append(cookie)

    # patchright expects { "cookies": [...], "origins": [...] }
    state = {
        "cookies": fixed_cookies,
        "origins": []
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(state, f, indent=2)

    print(f"✅ Saved state to: {output_path}")
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Import cookies to state.json")
    parser.add_argument("--cookies", required=True, help="Path to cookies JSON file")
    parser.add_argument("--output", help="Output path (default: data/browser_state/state.json)")

    args = parser.parse_args()

    # Get output path
    if args.output:
        output_path = Path(args.output)
    else:
        script_dir = Path(__file__).parent
        skill_dir = script_dir.parent
        output_path = skill_dir / "data" / "browser_state" / "state.json"

    # Load cookies
    with open(args.cookies, "r") as f:
        cookies = json.load(f)

    print(f"Loaded {len(cookies)} cookies from: {args.cookies}")

    # Convert and save
    convert_cookies_to_state(cookies, output_path)

    # Also save auth_info
    auth_info_path = output_path.parent.parent / "auth_info.json"
    auth_info = {
        "authenticated_at": 1745616000,  # Approximate current time
        "authenticated_at_iso": "2025-04-25 00:00:00",
        "imported": True
    }
    with open(auth_info_path, "w") as f:
        json.dump(auth_info, f, indent=2)

    print(f"✅ Import complete!")
    print(f"   State: {output_path}")
    print(f"   Auth info: {auth_info_path}")


if __name__ == "__main__":
    main()
