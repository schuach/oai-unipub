#! /bin/env python3

import os
import re
import shutil
import zipfile
import logging
from datetime import date


def get_filename(mods_path, journal):
    try:
        # git VLID from filename because it's not in the metadata.
        vlid = re.findall(r'(\d+)', mods_path)[-1]

        filename = f"{journal}_VLID{vlid}_{date.today().isoformat()}"
    except Exception as e:
        logging.error(f"Could not get filename for {os.path.basename(mods_path)}: {e}")
        filename = None

    print(filename)
    return filename


def make_zip(directories, journal):
    logging.info("Creating zip files")
    # make tuples of corresponding MODS and PDF filenames
    pairs = []
    src_dir = directories["HARVEST_DIR"]
    print(src_dir)
    fnames = os.listdir(src_dir)
    pdf_names = [fname for fname in fnames if fname.endswith("pdf")]

    # check for a MODS file with the same name as the PDF
    for pdf_name in pdf_names:
        mods_name = pdf_name[:-3] + "xml"
        if mods_name in fnames:
            pairs.append((os.path.join(src_dir, mods_name), os.path.join(src_dir, pdf_name)))

    for pair in pairs:
        mods_path, pdf_path = pair
        filename = get_filename(mods_path, journal)
        if filename:
            zipfile_name = os.path.join(directories["OUTPUT_DIR"], f'{filename}.zip')
            logging.debug(f"Creating ZIP file for {filename}")
            with zipfile.ZipFile(zipfile_name, mode="w") as out_zip:
                out_zip.write(mods_path, filename + ".xml")
                out_zip.write(pdf_path, filename + ".pdf")
        else:
            logging.error(f"No ZIP created for {os.path.basename(pdf_path)[:-3]}")
            shutil.move(mods_path, directories["ERROR_DIR"])
            shutil.move(pdf_path, directories["ERROR_DIR"])
