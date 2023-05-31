import argparse
import logging
import os
from datetime import datetime
from logging import config
import sys

from oaiharvest.harvest import main as harvest

from config import Config
from oai_unipub.get_pdfs import fetch_pdf
from oai_unipub.make_zip import make_zip
from oai_unipub.ftp_transfer import send_to_ftp

parser = argparse.ArgumentParser(prog="up2portico",
                                 description="Harvest metadata from unipub and ftp it to portico.")

parser.add_argument("operation",
                    metavar="operation",
                    type=str,
                    nargs="+",
                    help="operations to perform: all, harvest, get_pdf, make_zip, send_ftp",
                    choices=["all", "harvest", "get_pdf", "make_zip", "send_ftp"])

parser.add_argument("-j",
                    "--journals",
                    type=str,
                    nargs="+",
                    help="""Journals to harvest. For a list of journals run 'oai-reg list'""")

parser.add_argument("-f",
                    "--journal_file",
                    type=str,
                    help="A file with the journals to harvest. One journal per line.")

args = parser.parse_args()

LOG_FILE = "unipub-portico.log"


def logging_setup(log_file):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'logfile_formatter': {
                'format': '%(asctime)s %(levelname)s %(message)s',
            },
            'stderr_formatter': {
                'format': '%(levelname)s %(message)s',
            },
        },
        'handlers': {
            'stderr': {
                'class': 'logging.StreamHandler',
                'formatter': 'stderr_formatter',
                'level': 'INFO',
            },
            'log_file': {
                'class': 'logging.FileHandler',
                'filename': log_file,
                'mode': 'a',
                'formatter': 'logfile_formatter',
                'level': 'DEBUG',
            },
        },
        'loggers': {
            '': {
                'level': 'DEBUG',
                'handlers': ['stderr', 'log_file'],
            },
        },
    })


logging_setup(LOG_FILE)


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    logging.info(f"Starting up2portico at {timestamp}.")

    # get the journals to harvest
    if args.journal_file:
        with open(args.journal_file) as fh:
            journals = [journal.strip() for journal in fh
                        if not (journal.strip() == "" or journal.startswith("#"))]
    elif args.journals:
        journals = args.journals
    else:
        journals = []


    for journal in journals:
        # make directories needed for this run of this journal
        logging.debug(f"Creating directories for {journal}.")

        directories = {
            "HARVEST_DIR": os.path.join(Config.DATA_DIR, "NEW", journal),
            "OUTPUT_DIR": os.path.join(Config.DATA_DIR, "OUTPUT", journal),
            "SENT_DIR": os.path.join(Config.DATA_DIR, "SENT", journal, timestamp),
            "ERROR_DIR": os.path.join(Config.DATA_DIR, "ERRORS", journal, timestamp),
        }

        for directory in directories.values():
            os.makedirs(directory, exist_ok=True)

        # operate
        if "all" in args.operation or "harvest" in args.operation:
            harvest(f"--db registry.sqlite {journal}".split())
        if "all" in args.operation or "get_pdf" in args.operation:
            fetch_pdf(directories)
        if "all" in args.operation or "make_zip" in args.operation:
            make_zip(directories, journal)
        if "all" in args.operation or "send_ftp" in args.operation:
            send_to_ftp(directories)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.fatal(f"Exiting abnormally: {e}")
        sys.exit(1)
