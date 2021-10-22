#! /bin/env python3

import os
import shutil
import zipfile
import logging
from lxml import etree


def get_filename(mods_path):
    root = etree.parse(open(mods_path)).getroot()
    ns = {"mods": root.nsmap["mods"],
          "vl": root.nsmap["vl"]}

    host = '/mods:mods/mods:relatedItem[@type="host"]'
    journal_title = root.xpath(f'{host}/mods:titleInfo/mods:title', namespaces=ns)[0].text

    try:
        # check if it is an article
        if root.xpath('/mods:mods/mods:genre', namespaces=ns):
            date = root.xpath(f'{host}/mods:part/mods:date', namespaces=ns)[0].text
            vol = root.xpath(f'{host}/mods:part/mods:detail[@type="volume"]/mods:number', namespaces=ns)[0].text
            iss = root.xpath(f'{host}/mods:part/mods:detail[@type="issue"]/mods:number', namespaces=ns)[0].text
            startpage = root.xpath(f'{host}/mods:part/mods:extent/mods:start', namespaces=ns)[0].text
            try:
                vol = f"{int(vol):02}"
            except ValueError:
                vol = date
            filename = f"{journal_title}_{vol}_{date}_{iss}_{int(startpage):03}"
        # if not, it is an issue
        else:
            part = '/mods:mods/mods:part'
            date = root.xpath(f'{part}/mods:date', namespaces=ns)[0].text
            vol = root.xpath(f'{part}/mods:detail[@type="volume"]/mods:number', namespaces=ns)[0].text
            iss = root.xpath(f'{part}/mods:detail[@type="issue"]/mods:number', namespaces=ns)[0].text
            filename = f"{journal_title}_{int(vol):02}_{date}_{int(iss):02}_000"
    except Exception as e:
        logging.error(f"Could not get filename for {os.path.basename(mods_path)}: {e}")
        filename = None

    return filename


def make_zip(directories):
    logging.info("Creating zip files")
    # make tuples of corresponding MODS and PDF filenames
    pairs = []
    src_dir = directories["HARVEST_DIR"]
    fnames = os.listdir(src_dir)
    pdf_names = [fname for fname in fnames if fname.endswith("pdf")]

    # check for a MODS file with the same name as the PDF
    for pdf_name in pdf_names:
        mods_name = pdf_name[:-3] + "xml"
        if mods_name in fnames:
            pairs.append((os.path.join(src_dir, mods_name), os.path.join(src_dir, pdf_name)))

    for pair in pairs:
        mods_path, pdf_path = pair
        filename = get_filename(mods_path)
        if filename:
            zipfile_name = os.path.join(directories["OUTPUT_DIR"], f'MODS {filename}.zip')
            logging.debug(f"Creating ZIP file for {filename}")
            with zipfile.ZipFile(zipfile_name, mode="w") as out_zip:
                out_zip.write(mods_path, filename + ".xml")
                out_zip.write(pdf_path, filename + ".pdf")
        else:
            logging.error(f"No ZIP created for {os.path.basename(pdf_path)[:-3]}")
            shutil.move(mods_path, directories["ERROR_DIR"])
            shutil.move(pdf_path, directories["ERROR_DIR"])
