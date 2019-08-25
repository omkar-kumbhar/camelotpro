from .config import *

free_api_key = 'To use flavour "CamelotPro", a valid APIKey is needed.\n'\
               'The valid APIKey should be passed in "pro_kwargs" as {"api_key": <Valid API Key>}.\n' \
               'To receive a Free APIKey register at %s' % free_trail_url

try_pro = "[Info]: No tables were extracted from the basic camelot version.\n" \
          "Try CamelotPro version to extract tables from images/scan PDFs.\n" + free_api_key

valid_api_key = "Invalid APIKey.\n" + free_api_key

out_of_credits = f"[Info]: Your api_key is out of credits.\nPurchase more credits at {purchase_url}"


def notify(help_text):
    print("\n ".join(["#-#-" * 20, help_text, "#-#-" * 20]))
