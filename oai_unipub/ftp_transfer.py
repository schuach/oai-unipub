from ftplib import FTP
import os
import shutil
import logging
from config import Config


def send_to_ftp(directories):
    addr = Config.FTP_URL
    ftp_user = Config.FTP_USER
    ftp_pass = Config.FTP_PASS
    output_dir = directories["OUTPUT_DIR"]
    error_dir = directories["ERROR_DIR"]
    sent_dir = directories["SENT_DIR"]

    logging.debug(f"Connecting to {addr}")
    ftp = FTP(addr)
    ftp.login(ftp_user, ftp_pass)

    flst = os.listdir(output_dir)

    for fn in flst:
        logging.debug(f"Sending {fn} via FTP.")
        fpath = os.path.join(output_dir, fn)
        res = ftp.storbinary(f'STOR {fn}', open(fpath, "rb"))
        logging.debug(res)
        if "226 Transfer complete." in res:
            shutil.move(fpath, sent_dir)
        else:
            shutil.move(fpath, error_dir)
            logging.error(f"{res}")

    ftp.quit()
