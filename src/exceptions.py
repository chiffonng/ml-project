import sys
from src.logger import logging

def get_error_message(error, error_detail:sys):
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    
    error_message = f"Error in python file '{file_name}' at line {exc_tb.tb_lineno}: {error}"
    
    return error_message

class CustomException(Exception):
    """Base class for other exceptions"""
    def __init__(self, error, error_detail:sys):
        super().__init__(error)
        self.error_message = get_error_message(error, error_detail)
        
    def __str__(self):
        return self.error_message