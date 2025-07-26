#!/usr/bin/env python3
"""Hook script for running lint and type checking with auto-fix attempts."""

import subprocess
import sys
from typing import List, Tuple


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def run_black_fix() -> bool:
    """Run black formatter to fix style issues."""
    print("🔧 Running black formatter...")
    code, stdout, stderr = run_command(
        ["black", "massgen", "tests", "--exclude", "future_mass"]
    )
    if code == 0:
        print("✅ Black formatting complete")
        return True
    else:
        print(f"❌ Black failed: {stderr}")
        return False


def run_isort_fix() -> bool:
    """Run isort to fix import ordering."""
    print("🔧 Running isort...")
    code, stdout, stderr = run_command(
        ["isort", "massgen", "tests", "--skip", "future_mass"]
    )
    if code == 0:
        print("✅ Import sorting complete")
        return True
    else:
        print(f"❌ Isort failed: {stderr}")
        return False


def run_flake8_check() -> Tuple[bool, List[str]]:
    """Run flake8 and return status and errors."""
    print("🔍 Running flake8 check...")
    code, stdout, stderr = run_command(["flake8", "massgen", "tests"])
    if code == 0:
        print("✅ Flake8 check passed")
        return True, []
    else:
        errors = stdout.strip().split("\n") if stdout else []
        print(f"❌ Flake8 found {len(errors)} issues")
        return False, errors


def run_mypy_check() -> Tuple[bool, List[str]]:
    """Run mypy type checking."""
    print("🔍 Running mypy type check...")
    code, stdout, stderr = run_command(
        ["mypy", "massgen", "--config-file", "pyproject.toml"]
    )
    if code == 0:
        print("✅ Type checking passed")
        return True, []
    else:
        errors = stdout.strip().split("\n") if stdout else []
        print(f"❌ Mypy found {len(errors)} type errors")
        return False, errors


def main() -> int:
    """Main hook function with auto-fix attempts."""
    print("\n🚀 Starting lint and type check hook...\n")

    max_iterations = 3
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n📍 Iteration {iteration}/{max_iterations}")

        # Run auto-fixers first
        run_black_fix()
        run_isort_fix()

        # Check for remaining issues
        flake8_success, flake8_errors = run_flake8_check()
        mypy_success, mypy_errors = run_mypy_check()

        # If everything passes, we're done
        if flake8_success and mypy_success:
            print("\n✨ All checks passed!")
            return 0

        # If we're on the last iteration, report unfixed errors
        if iteration == max_iterations:
            print("\n⚠️  Could not fix all issues after 3 iterations:")

            if flake8_errors:
                print("\n🔴 Remaining flake8 errors:")
                for error in flake8_errors[:10]:  # Show first 10 errors
                    print(f"  {error}")
                if len(flake8_errors) > 10:
                    print(f"  ... and {len(flake8_errors) - 10} more")

            if mypy_errors:
                print("\n🔴 Remaining mypy errors:")
                for error in mypy_errors[:10]:  # Show first 10 errors
                    print(f"  {error}")
                if len(mypy_errors) > 10:
                    print(f"  ... and {len(mypy_errors) - 10} more")

            print("\n💡 Please fix these issues manually.")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
