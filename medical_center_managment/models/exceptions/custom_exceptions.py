import warnings
from odoo import _
import logging
from inspect import currentframe
from odoo.tools.func import frame_codeinfo
from odoo.exceptions import UserError
import datetime
_logger = logging.getLogger(__name__)

class InvalidMeeting(UserError):
    """Exception raised for trying to reserve doctor time when the doctor is not available .

    Attributes:
        doctor -- The doctor you are trying to reserve meeting with
        reason -- the reason could be: the doctor has another meeting in that time, or 
        he is not available
        
    """

    def __init__(self, doctor, type, meeting=False, valid_times = False):
        
        self.doctor = doctor
        if type == "another_meeting" and meeting:
            message = _(f"The doctor has another meeting in {meeting.address_id.name} with {meeting.patient_id.name}")
        else:
            message = _(f"The doctor is not available at this time")
        self.message = message
        self.title = "Title"
        self.doctor_id = doctor.id
        self.date = meeting.start_date.date() if meeting else False
        self.time_start = datetime.time(hour=0, minute=0)
        self.time_end = datetime.time(hour=23, minute=59)
        value = {
            "valid_time" : valid_times
            
        }
        
        super(UserError, self).__init__(message, value=valid_times)    
