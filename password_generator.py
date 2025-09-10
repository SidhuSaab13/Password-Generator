from __future__ import annotations

from pathlib import Path
from datetime import datetime
import random
import string
import secrets
import argparse
from typing import Iterable, List

ROOT = Path(__file__).parent
MEMORABLE_DIR = ROOT / "Memorable"
RANDOM_DIR = ROOT / "Random"
MEMORABLE_LOG = MEMORABLE_DIR / "Generated_Passwords.txt"
RANDOM_LOG = RANDOM_DIR / "Generated_Passwords.txt"

NOUNS_PATH = ROOT / "top_english_nouns_lower_100000.txt"


def ensure_dirs() -> None:
    MEMORABLE_DIR.mkdir(parents=True, exist_ok=True)
    RANDOM_DIR.mkdir(parents=True, exist_ok=True)


def timestamp() -> str:
    return datetime.now().strftime("%a %b %d %Y %H:%M:%S")


def append_log(log_path: Path, password: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp()}  |  {password}\n")


def load_nouns(limit: int | None = None) -> List[str]:
    with open(NOUNS_PATH, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
    if limit is not None:
        words = words[:limit]
    return words


def generate_memorable(
    n_words: int = 4,
    case: str = "lower",
    add_digit_each: bool = True,
    nouns_pool: Iterable[str] | None = None,
) -> str:
    if n_words <= 0:
        raise ValueError("n_words must be >= 1.")
    if nouns_pool is None:
        nouns_pool = load_nouns()
    pool = list(nouns_pool)
    if n_words > len(pool):
        raise ValueError("n_words is larger than the nouns list.")
    words = random.sample(pool, k=n_words)

    def apply_case(w: str) -> str:
        if case == "lower":
            return w.lower()
        if case == "upper":
            return w.upper()
        if case == "title":
            return w.title()
        if case == "mixed":
            return random.choice([w.lower(), w.upper(), w.title()])
        raise ValueError("case must be 'lower', 'upper', 'title', or 'mixed'")

    processed = []
    for w in words:
        w2 = apply_case(w)
        if add_digit_each:
            w2 = f"{w2}{secrets.choice(string.digits)}"
        processed.append(w2)

    pwd = "-".join(processed)
    append_log(MEMORABLE_LOG, pwd)
    return pwd


def generate_random(
    length: int = 16,
    include_punct: bool = True,
    forbidden: Iterable[str] | None = None,
) -> str:
    if length <= 0:
        raise ValueError("length must be >= 1.")

    alphabet = set(string.ascii_lowercase + string.ascii_uppercase + string.digits)
    if include_punct:
        alphabet |= set(string.punctuation)
    if forbidden:
        alphabet -= set(forbidden)

    if not alphabet:
        raise ValueError("No characters available to generate password.")

    alphabet = "".join(sorted(alphabet))
    pwd = "".join(secrets.choice(alphabet) for _ in range(length))
    append_log(RANDOM_LOG, pwd)
    return pwd


def generate_1000_mixed() -> None:
    """Generate 1000 passwords, randomly mixing memorable and random."""
    ensure_dirs()
    for _ in range(1000):
        if random.random() < 0.5:
            n = random.choice([3, 4, 5])
            c = random.choice(["lower", "upper", "title", "mixed"])
            generate_memorable(n_words=n, case=c, add_digit_each=True)
        else:
            L = random.choice([12, 14, 16, 20])
            include_punct = random.choice([True, False])
            forbidden = set("O0Il|`'\" ")
            generate_random(length=L, include_punct=include_punct, forbidden=forbidden)


def main():
    parser = argparse.ArgumentParser(
        description="Password Generator (memorable or random) + logging with timestamp."
    )
    # ⬇️ Not required anymore so Play button won't error
    sub = parser.add_subparsers(dest="mode")

    # memorable
    p_mem = sub.add_parser("memorable", help="generate memorable password")
    p_mem.add_argument("--n_words", type=int, default=4, help="number of words.")
    p_mem.add_argument(
        "--case",
        type=str,
        default="lower",
        choices=["lower", "upper", "title", "mixed"],
        help="letter case for words.",
    )
    p_mem.add_argument(
        "--no_digit",
        action="store_true",
        help="do not add a digit to each word.",
    )

    # random
    p_rand = sub.add_parser("random", help="generate random password")
    p_rand.add_argument("--length", type=int, default=16, help="length of password.")
    p_rand.add_argument(
        "--no_punct",
        action="store_true",
        help="do not include punctuation characters.",
    )
    p_rand.add_argument(
        "--forbidden",
        type=str,
        default="",
        help='characters to exclude, e.g. "O0Il|`\' \\""',
    )

    sub.add_parser("stress", help="generate 1000 mixed passwords.")

    args = parser.parse_args()
    ensure_dirs()

    # ⬇️ Fallback prompt when launched with no args (Play button)
    if args.mode is None:
        choice = input("Choose mode [memorable/random/stress] (default: memorable): ").strip().lower()
        if choice == "":
            choice = "memorable"
        if choice not in {"memorable", "random", "stress"}:
            print("Invalid choice.")
            return
        args.mode = choice

    if args.mode == "memorable":
        pwd = generate_memorable(
            n_words=getattr(args, "n_words", 4),
            case=getattr(args, "case", "lower"),
            add_digit_each=not getattr(args, "no_digit", False),
        )
        print(pwd)

    elif args.mode == "random":
        pwd = generate_random(
            length=getattr(args, "length", 16),
            include_punct=not getattr(args, "no_punct", False),
            forbidden=list(getattr(args, "forbidden", "")) if getattr(args, "forbidden", "") else None,
        )
        print(pwd)

    elif args.mode == "stress":
        generate_1000_mixed()
        print("Generated 1000 mixed passwords.")


if __name__ == "__main__":
    main()
