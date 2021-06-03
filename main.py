import functools
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import click


def normalize_paths(paths: List[str]) -> List[Path]:
    norm_paths = []

    for path in paths:
        path = Path(path)
        if not path.is_absolute():
            path = path.resolve()

        norm_paths.append(path)

    return norm_paths


def group_files_by_name(
        dir_paths: List[Path],
        full_depth: bool,
        ignore_substr: Optional[str]
) -> Tuple[Dict[str, List[Path]], Dict[str, List[Path]]]:
    strict_stat = dict()
    fuzzy_stat = dict()
    search_glob = "**/*" if full_depth else "*"

    for dir_path in dir_paths:
        for fpath in dir_path.glob(search_glob):
            if not fpath.is_dir():
                if ignore_substr:
                    fuzzy_name = fpath.name.replace(ignore_substr, "")
                    fuzzy_stat.setdefault(fuzzy_name, []).append(fpath)

                strict_stat.setdefault(fpath.name, []).append(fpath)

    return strict_stat, fuzzy_stat


def find_duplicates(stat: Dict[str, List[Path]], caption: str = "Duplicates:"):
    print("\n")
    print("=" * 10)
    print(caption)
    print("=" * 10)

    total_files = functools.reduce(lambda total, dups: total + len(dups), stat.values(), 0)
    print(f"Total files count: {total_files}\n")

    duplicates = {k: v for k, v in stat.items() if len(v) > 1}
    if duplicates:
        for fname, fpaths in sorted(duplicates.items()):
            print(f"\n{fname}:")
            print("\n".join([str(path) for path in sorted(fpaths)]))
    else:
        print("DUPLICATES NOT FOUND")


@click.command()
@click.argument('input_dirs', type=str, nargs=-1, required=True)
@click.option("--full_depth", type=bool, default=True, help="if False ignores files from subdirs")
@click.option("--ignore_substr", type=str, default=None, help="ignores this substring when compare file names")
def main(input_dirs, full_depth, ignore_substr):
    dir_paths = normalize_paths(input_dirs)
    strict_stat, fuzzy_stat = group_files_by_name(dir_paths, full_depth, ignore_substr)

    find_duplicates(strict_stat, "Strict duplicates")
    if ignore_substr:
        find_duplicates(fuzzy_stat, f"Fuzzy duplicates (ignore `{ignore_substr}` substr)")


if __name__ == '__main__':
    main()
