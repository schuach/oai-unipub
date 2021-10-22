#! /bin/env python3

import os
import shutil
import re
import logging
import requests


def download_pdf(filename, directories):
    vlid = re.search(r':([0-9]+)\.mods\.xml', filename).groups()[0]
    url = f"https://unipub.uni-graz.at/download/pdf/{vlid}"

    pdfname = filename[:-3] + "pdf"
    if os.path.isfile(pdfname):
        logging.warning(f"PDF file already exists. {vlid}")
        return
    else:
        res = requests.get(url)

    try:
        res.raise_for_status()
    except Exception as e:
        logging.error(f"Can't get PDF {url}. Exception: {e}")
        shutil.move(filename, os.path.join(directories["ERROR_DIR"]))
        return

    with open(pdfname, "wb") as fh:
        fh.write(res.content)


def fetch_pdf(directories):
    harvest_dir = directories["HARVEST_DIR"]
    articles_mods = os.listdir(harvest_dir)
    logging.info("Getting PDF files.")
    for article in articles_mods:
        if not article.endswith(".mods.xml"):
            continue
        else:
            download_pdf(os.path.join(harvest_dir, article), directories)
