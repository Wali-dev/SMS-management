from urllib import response

class SendSMS:
    def init(self,phone_number,proxy):
        self.phone_number = phone_number
        self.proxy = proxy

    def SendOtp(self):
        # this function sends message on the phone number using that proxy
        if 'sent successfully' in response.text:
            return True
        else:
            return False
class SubmitSMS:
    def SumitOtp(self,trigger_id,SMS_code):
        # submits the SMS_code
        if 'submitted successfully' in response.text:
            return True
        else:
            return False