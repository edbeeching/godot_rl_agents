import argparse
from godot_rl.wrappers.sample_factory_wrapper import sample_factory_training, sample_factory_enjoy


def get_args():
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--env_path", default=None, type=str, help="Godot binary to use")
    parser.add_argument("--eval", default=False, action="store_true", help="whether to eval the model")
    parser.add_argument("--speedup", default=1, type=int, help="whether to speed up the physics in the env")
    parser.add_argument("--export", default=False, action="store_true", help="wheter to export the model")
    parser.add_argument("--viz", default=False, action="store_true", help="Whether to visualize one process")

    return parser.parse_known_args()



def main():
    args, extras = get_args()
    if args.eval:
        sample_factory_enjoy(args, extras)
    else:
        sample_factory_training(args, extras)
        
        
if __name__ == "__main__":
    main()