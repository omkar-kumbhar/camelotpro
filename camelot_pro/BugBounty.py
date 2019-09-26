"""
For now, this handsover informative message to the user based on the respone.
To add bug bounty program by default in future
"""
# TODO. Generate a private presigned URL to PUT OBJECT from demo users


class HandleResponse:
    def __init__(self, recieved_response):
        self.resp = recieved_response
        status_code = self.resp.status_code
        if status_code in range(200, 202):
            pass
        elif status_code in range(400, 500):
            print("-=- "*15)
            print("[Info]: Complete response content below: \n", self.resp.content)
            err_msg = "You missed something. Check the complete return response above"
            print(err_msg)
            raise ConnectionRefusedError(err_msg)
        elif status_code in range(500, 599):
            print("-=- "*15)
            print("[Info]: Complete response content below: \n", self.resp.content)
            print("Check the complete return response above for you reference")
            err_msg = "Woahhh!! Not you, we messed it. We are already alerted"
            print(err_msg)
            raise ConnectionError(err_msg)
