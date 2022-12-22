import argparse
import os
from huggingface_hub import Repository


def load_from_hf(dir_path: str, repo_id: str):
    temp = repo_id.split("/")
    repo_name = temp[1]

    local_dir = os.path.join(dir_path, repo_name)
    Repository(local_dir, repo_id, repo_type="dataset")
    print(f"The repository {repo_id} has been cloned to {local_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--hf_repository",
        help="Repo id of the dataset / environment repository from the Hugging Face Hub in the form user_name/repo_name",
        type=str,
    )
    parser.add_argument(
        "-d",
        "--example_dir",
        help="Local destination of the repository. Will save repo to examples/repo_name",
        type=str,
        default="./examples",
    )
    args = parser.parse_args()

    load_from_hf(args.example_dir, args.hf_repository)


if __name__ == "__main__":
    main()
