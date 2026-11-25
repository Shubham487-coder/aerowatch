"""Pre-commit guard: block any commit not made with the personal email."""

import subprocess
import sys

EXPECTED = "shubhamshrm487@gmail.com"


def main() -> int:
    command = ["git", "config", "user.email"]  # noqa: S607  (git is found on PATH on purpose)
    result = subprocess.run(command, capture_output=True, text=True, check=False)  # noqa: S603
    email = result.stdout.strip()
    if email != EXPECTED:
        print(f"Blocked: this repo must be committed as {EXPECTED}, but git would use '{email}'.")
        print(f'Fix: git config user.email "{EXPECTED}"')
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
