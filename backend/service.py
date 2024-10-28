# service.py
from program import SendSMS, SubmitSMS
from models import SmsStats, MongoPair
from config import db_SQL, db_mongo
import pandas as pd
import time
from collections import defaultdict
from datetime import datetime, timedelta
from threading import Thread
import threading

class SMSService:
    # Track running pairs and their threads
    running_pairs = {}
    # Track send times for rate limiting
    send_times = defaultdict(list)
    
    def __init__(self, pair_name):
        self.pair_name = pair_name
        self.should_stop = False
        # Get pair details from MongoDB
        pair_data = MongoPair.collection.find_one({"pair_name": pair_name})
        if not pair_data:
            raise ValueError("Pair not found")
        
        self.proxy = pair_data.get("proxy")
        self.session_details = pair_data.get("session_details")
        self.numbers_file = self.session_details.get("numbers_file")
    
    @classmethod
    def start_pair(cls, pair_name):
        """Start processing for a pair"""
        if pair_name in cls.running_pairs:
            return {"success": False, "message": "Pair is already running"}
            
        # Update pair status in MongoDB
        MongoPair.collection.update_one(
            {"pair_name": pair_name},
            {"$set": {"active_status": True}}
        )
        
        service = cls(pair_name)
        thread = Thread(target=service.process_numbers)
        thread.daemon = True
        thread.start()
        
        cls.running_pairs[pair_name] = service
        return {"success": True, "message": f"Started processing pair {pair_name}"}
    
    @classmethod
    def stop_pair(cls, pair_name):
        """Stop processing for a pair"""
        if pair_name not in cls.running_pairs:
            return {"success": False, "message": "Pair is not running"}
        
        service = cls.running_pairs[pair_name]
        service.should_stop = True
        
        # Update pair status in MongoDB
        MongoPair.collection.update_one(
            {"pair_name": pair_name},
            {"$set": {"active_status": False}}
        )
        
        del cls.running_pairs[pair_name]
        return {"success": True, "message": f"Stopped processing pair {pair_name}"}
    
    @classmethod
    def restart_pair(cls, pair_name):
        """Restart processing for a pair"""
        stop_result = cls.stop_pair(pair_name)
        time.sleep(1)  # Give it a moment to stop
        start_result = cls.start_pair(pair_name)
        
        return {
            "success": start_result["success"],
            "message": f"Restarted pair {pair_name}"
        }
    
    def can_send_sms(self):
        """Check if we can send SMS based on rate limit (10 per minute)"""
        current_time = datetime.now()
        minute_ago = current_time - timedelta(minutes=1)
        
        # Clean up old entries
        self.send_times[self.pair_name] = [
            t for t in self.send_times[self.pair_name] 
            if t > minute_ago
        ]
        
        return len(self.send_times[self.pair_name]) < 10
    
    def process_numbers(self):
        """Process phone numbers from Excel file"""
        try:
            # Read numbers from Excel file
            df = pd.read_excel(self.numbers_file)
            phone_numbers = df['phone_number'].tolist()  # Adjust column name as needed
            
            for phone_number in phone_numbers:
                # Check if stop was requested
                if self.should_stop:
                    break
                    
                # Check rate limit
                while not self.can_send_sms() and not self.should_stop:
                    time.sleep(1)
                
                if self.should_stop:
                    break
                
                # Process single SMS
                self.process_single_sms(phone_number)
                
                # Update send times
                self.send_times[self.pair_name].append(datetime.now())
                
        except Exception as e:
            MongoPair.collection.update_one(
                {"pair_name": self.pair_name},
                {"$set": {"active_status": False}}
            )
            if self.pair_name in self.running_pairs:
                del self.running_pairs[self.pair_name]
    
    def process_single_sms(self, phone_number):
        """Process a single SMS"""
        try:
            sms_sender = SendSMS(phone_number, self.proxy)
            sms_submitter = SubmitSMS()
            
            send_result = sms_sender.SendOtp()
            
            if send_result:
                trigger_id = "some_trigger_id"  # You'll need to implement how to get this
                sms_code = "some_sms_code"     # You'll need to implement how to get this
                submit_result = sms_submitter.SumitOtp(trigger_id, sms_code)
            else:
                submit_result = False
            
            self._update_stats(send_result, submit_result)
            
        except Exception as e:
            self._update_stats(False, False)
    
    def _update_stats(self, send_success, submit_success):
        """Update statistics for a single SMS"""
        try:
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
            
            if send_success:
                stats.total_sms_sent += 1
            else:
                stats.total_sms_failed += 1
            
            total_attempts = stats.total_sms_sent + stats.total_sms_failed
            stats.total_rate_of_success = (stats.total_sms_sent * 100) // total_attempts
            stats.total_rate_of_failure = (stats.total_sms_failed * 100) // total_attempts
            
            db_SQL.session.commit()
            
        except Exception as e:
            db_SQL.session.rollback()
            raise