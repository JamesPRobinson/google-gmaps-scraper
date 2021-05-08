from argparse import ArgumentParser
from scraper.gmaps.run_gmaps import run_gmaps

# TODO this command should call the wrapper function, right now we don't have
# such wrapper function so we are calling run_gmaps
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "-f", "--file", dest='file_path', help="path to excel file"
        )
    parser.add_argument(
        "-s", "--size", dest="size", type=int, default=100,
        help="Size of queue buffer, e.g. the limit reached before parsing emails from websites scrapes"
        )

    # Gets the parsed arguments as a dictionary
    kwargs = vars(parser.parse_args())

    run_gmaps(**kwargs)
