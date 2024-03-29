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

                "dup_check": bool, default: False - to bypass the duplicate check
                    Useful to handle duplicate requests, check based on the FileName

                "wait_for_output": bool, default: True
                    Loops and check for the output for a maximum of 300 seconds, before the process exits as an output.
                    with 20 second gap in between retries
                        - If the process will return the output before 300 seconds, when the processing is successful
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
            gp_resp = gone_pro.trigger(filepath, pages, password=password, dup_check=pro_kwargs.get("dup_check", False))
        else:
            gp_resp = gone_pro.get_tables(pro_kwargs["job_id"])

        # Added default wait time, because early users are confused of no output
        pro_kwargs["wait_for_output"] = pro_kwargs.get("wait_for_output", True)

        if gp_resp["JobStatus"].lower().startswith("process") and pro_kwargs["wait_for_output"]:
            max_wait = 300
            check_freq = 20
            while max_wait > 0 and gp_resp["JobStatus"].lower().startswith("process"):
                print(f'[Info]: Please wait, the Job is: {gp_resp["JobStatus"]} ..')
                max_wait -= check_freq
                time.sleep(check_freq)
                gp_resp = gone_pro.get_tables(job_id=gp_resp["JobId"])
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
