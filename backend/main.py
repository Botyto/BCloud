from argparse import ArgumentParser

from core.main import start
from core.main import MigrationAction, run_migration, run_app, run_jsschema

parser = ArgumentParser(
    prog="Backend server",
    description="Backend server")
parser.add_argument("-m", dest="migration", required=False, type=str, choices=[action.value for action in MigrationAction])
parser.add_argument("-t", dest="title", required=False, type=str)
args = parser.parse_args()

if __name__ == '__main__':
    if args.migration:
        action = MigrationAction(args.migration)
        start(run_migration, action, args.title)
    else:
        start(run_app)
