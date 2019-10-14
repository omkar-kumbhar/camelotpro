# -*- coding: utf-8 -*-
from .helpers import *
from ExtractTable import ExtractTable

API_KEY = ""


def check_usage(api_key):
    return ExtractTable(api_key).check_usage()


def read_pdf(
        filepath,
        pages: str = "1",
        password: str = '',
        flavor: str = "camelotPro",
        suppress_stdout: bool = False,
        layout_kwargs: dict = None,
        pro_kwargs: dict = None,
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

                "max_wait_time": bool, default: True
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
        from .handlers import PDFSpliter
        from camelot_pro.doppelganger import table_list

        et_sess = ExtractTable(api_key=pro_kwargs["api_key"] if pro_kwargs.get("api_key", "") else API_KEY)
        max_wait_time = int(pro_kwargs.get("max_wait_time", 300))
        if not pro_kwargs.get("job_id", ""):
            with PDFSpliter(filepath, pages, password) as pdf_obj:
                et_sess.process_file(pdf_obj.filepath, dup_check=pro_kwargs.get("dup_check", ""), max_wait_time=max_wait_time)
        else:
            et_sess.get_result(pro_kwargs["job_id"], max_wait_time=max_wait_time)

        gp_resp = et_sess.ServerResponse.json()
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
