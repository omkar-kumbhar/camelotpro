# -*- coding: utf-8 -*-
import math
import time

from .helpers import *


def read_pdf(
        filepath,
        pages="1",
        password=None,
        flavor="lattice",
        suppress_stdout=False,
        layout_kwargs={},
        pro_kwargs=None,
        **kwargs
):
    """
    Read PDF and return extracted tables.
    Parameters described below are exclusive for CamelotPro.
    Please refer to the docstrings from Camelot.read_pdf for information on other parameters
    <https://github.com/atlanhq/camelot/blob/master/camelot/io.py#L9>

    Parameters
    ----------
    flavor : str (default: 'lattice') [Case-Insensitive]
        The parsing method to use ('lattice' or 'stream' or 'CamelotPro').

    pro_kwargs: dict, Must Need (if flavor is "CamelotPro")
        A dict of (
            {
                "api_key": str,
                Mandatory, to trigger "CamelotPro" flavor, to process Scan PDFs and images, also text PDF files

                "job_id": str,
                    optional, if processing a new file
                    Mandatory, to retrieve the result of already submitted file

                "dup_check": bool, default: True
                    Useful to handle duplicate requests, check based on the FileName
                    False, to bypass the duplicate check

                "wait_time": int, in seconds [10, 90]
                    Maximum wait time, in seconds, before the process exits as an output.
                    Adds a wait time at the client-side to retry for a maximum of 4 times,
                    with at least 10 second gap in between retries
                        - If the process is successful before the 4 retries, the process will return the output
                        - Alternatively, a big file process can always be tracked using the ".JobId" from the output
            }
        )

    Returns
    -------
    tables : camelot.core.TableList
    """
    if pro_kwargs is None:
        pro_kwargs = {}
    flavor = flavor.lower()
    if flavor == "camelotpro":
        from camelot_pro.gopro import GoPro
        from camelot_pro.doppelganger import table_list
        going_pro = GoPro(pro_kwargs.get("api_key", ""))
        gone_pro = going_pro.validate_api_key()
        if not pro_kwargs.get("job_id", ""):
            gp_resp = gone_pro.trigger(filepath, pages, password=password, dup_check=pro_kwargs.get("dup_check", True))
        else:
            gp_resp = gone_pro.get_tables(pro_kwargs["job_id"])

        if not gp_resp["JobStatus"].lower().startswith("succe") and pro_kwargs.get("wait_time", 0):
            wait_time = min(int(pro_kwargs["wait_time"]), 90)
            check_freq = max(math.ceil(wait_time/4), 10)
            for _ in range(math.ceil(wait_time/check_freq)):
                time.sleep(check_freq)
                gp_resp = gone_pro.get_tables(job_id=gp_resp["JobId"])
                if gp_resp["JobStatus"].lower().endswith("succes"):
                    break
        tables = table_list(gp_resp)
    else:
        from camelot.io import read_pdf
        tables = read_pdf(
            filepath=filepath,
            pages=pages,
            password=password,
            flavor=flavor,
            suppress_stdout=suppress_stdout,
            layout_kwargs=layout_kwargs,
            **kwargs
        )
        if not tables:
            notify(try_pro)
    return tables
