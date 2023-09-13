from argparse import ArgumentParser

from core.data.sql.migrations import MigrationAction
from core import main

parser = ArgumentParser(
    prog="Backend server",
    description="Backend server")
parser.add_argument("-m", "--migration",
    dest="migration",
    required=False,
    type=str,
    choices=[action.value for action in MigrationAction])
args = parser.parse_args()

if __name__ == '__main__':
    if args.migration:
        action = MigrationAction(args.migration)
        main.run_migration(action)
    else:
        main.run_app()
