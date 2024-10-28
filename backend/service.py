# service.py
from program import SendSMS, SubmitSMS
from models import SmsStats
from config import db_SQL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self, pair_name, phone_number, proxy):
        self.pair_name = pair_name
        self.phone_number = phone_number
        self.proxy = proxy
        self.sms_sender = SendSMS(phone_number, proxy)
        self.sms_submitter = SubmitSMS()
        
    def process_sms_flow(self, trigger_id, sms_code):
        try:
            # Step 1: Send OTP
            send_result = self.sms_sender.SendOtp()
            
            # Step 2: Submit OTP if sending was successful
            if send_result:
                submit_result = self.sms_submitter.SumitOtp(trigger_id, sms_code)
            else:
                submit_result = False
                
            # Step 3: Update statistics
            self._update_stats(send_result, submit_result)
            
            return {
                "success": submit_result,
                "message": "SMS flow completed successfully" if submit_result else "SMS flow failed"
            }
            
        except Exception as e:
            logger.error(f"Error in SMS flow: {str(e)}")
            self._update_stats(False, False)
            return {
                "success": False,
                "message": f"Error occurred: {str(e)}"
            }
    
    def _update_stats(self, send_success, submit_success):
        try:
            # Get existing stats or create new
            stats = SmsStats.query.filter_by(pair_name=self.pair_name).first()
            
            if not stats:
                stats = SmsStats(
                    pair_name=self.pair_name,
                    total_sms_sent=0,
                    total_sms_failed=0,
                    total_rate_of_success=0,
                    total_rate_of_failure=0
                )
                db_SQL.session.add(stats)
            
            # Update statistics
            if send_success:
                stats.total_sms_sent += 1
            else:
                stats.total_sms_failed += 1
                
            # Calculate rates
            total_attempts = stats.total_sms_sent + stats.total_sms_failed
            if total_attempts > 0:
                stats.total_rate_of_success = (stats.total_sms_sent * 100) // total_attempts
                stats.total_rate_of_failure = (stats.total_sms_failed * 100) // total_attempts
            
            db_SQL.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating stats: {str(e)}")
            db_SQL.session.rollback()
            raise