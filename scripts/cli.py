import argparse
from scripts.main import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="QueryCon CLI")
    parser.add_argument("url", help="YouTube playlist URL")
    parser.add_argument("--summarize", action="store_true", help="Run summarization")
    parser.add_argument("--embed", action="store_true", help="Run embedding")
    args = parser.parse_args()

    run_pipeline(
        conference_url=args.url, do_summarize=args.summarize, do_embed=args.embed
    )


if __name__ == "__main__":
    main()
