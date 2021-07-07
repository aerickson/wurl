import argparse
import sys

from ..__about__ import __version__
from .._main import (
    categorize_urls,
    filter_allow_ignore,
    find_files,
    find_urls,
    print_to_screen,
    read_config,
)


def check(argv=None):
    # Parse command line arguments.
    parser = _get_parser()
    args = parser.parse_args(argv)

    # get non-hidden files in non-hidden directories
    files = find_files(args.paths)

    # filter files by allow-ignore-lists
    allow_files = set() if args.allow_files is None else args.allow_files
    ignore_files = set() if args.ignore_files is None else args.ignore_files

    d = read_config()
    if "allow_files" in d:
        allow_files = allow_files.union(set(d["allow_files"]))
    if "ignore_files" in d:
        ignore_files = ignore_files.union(set(d["ignore_files"]))

    files, _ = filter_allow_ignore(files, allow_files, ignore_files)

    urls = find_urls(files)
    urls, ignored_urls = filter_allow_ignore(
        urls,
        set() if args.allow_urls is None else set(args.allow_urls),
        set() if args.ignore_urls is None else set(args.ignore_urls),
    )

    print(
        f"Found {len(urls)} unique URLs in {len(files)} files "
        f"(ignored {len(ignored_urls)})"
    )
    d = categorize_urls(
        urls, args.timeout, args.max_connections, args.max_keepalive_connections
    )

    print_to_screen(d)
    has_errors = any(
        len(d[key]) > 0
        for key in ["Client errors", "Server errors", "Timeouts", "Other errors"]
    )
    return 1 if has_errors else 0


def _get_parser():
    parser = argparse.ArgumentParser(
        description=("Check URLs in text files."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("paths", type=str, nargs="+", help="files or paths to check")
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="connection timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "-c",
        "--max-connections",
        type=int,
        default=100,
        help="maximum number of allowable connections (default: 100)",
    )
    parser.add_argument(
        "-k",
        "--max-keepalive-connections",
        type=int,
        default=10,
        help="number of allowable keep-alive connections (default: 10)",
    )
    parser.add_argument(
        "-a",
        "--allow-urls",
        type=str,
        nargs="+",
        help="only consider URLs containing these strings (e.g., http:)",
    )
    parser.add_argument(
        "-i",
        "--ignore-urls",
        type=str,
        nargs="+",
        help="ignore URLs containing these strings (e.g., github.com)",
    )
    parser.add_argument(
        "-af",
        "--allow-files",
        type=str,
        nargs="+",
        help="only consider file names containing these strings (e.g., .txt)",
    )
    parser.add_argument(
        "-if",
        "--ignore-files",
        type=str,
        nargs="+",
        help="ignore file names containing these strings (e.g., .svg)",
    )

    __copyright__ = "Copyright (c) 2021 Nico Schlömer <nico.schloemer@gmail.com>"
    version_text = "\n".join(
        [
            "deadlink {} [Python {}.{}.{}]".format(
                __version__,
                sys.version_info.major,
                sys.version_info.minor,
                sys.version_info.micro,
            ),
            __copyright__,
        ]
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=version_text,
        help="display version information",
    )

    return parser
