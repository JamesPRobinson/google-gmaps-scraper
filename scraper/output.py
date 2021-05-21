import csv
from chardet import detect
import json
import logging
import requests
from .config import RES_FOLDER
from .email import get_email


FIELDS = ['locality', 'service', 'GMAPS-service', 'query', 'company_name', 'company_url', 'address', 'email', 'phone']
DEFAULT_ENCODING = 'utf-8'


def get_encoding(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    try:
        encoding_type = detect(rawdata)['encoding']
    except KeyError:
        return DEFAULT_ENCODING
    return encoding_type if not None else DEFAULT_ENCODING


class Output:
    def __init__(self, event):
        self.encoding = DEFAULT_ENCODING # unless otherwise stated
        self.event = event


    def process(self, record):
        try:          
            service_name = record['service']                       
            raw_output_filepath = str(RES_FOLDER.absolute() / ('GMAPS-' + service_name + '.csv'))
            
            with open(raw_output_filepath, mode='a', newline='', encoding=self.encoding) as raw_output_file:
                raw_writer = csv.DictWriter(raw_output_file, fieldnames=FIELDS)
                if raw_output_file.tell() == 0:
                    raw_writer.writeheader()
                if record['website']:
                    record['email'] = get_email(record['website'])
                raw_writer.writerow({'locality': record['city'], 'service': service_name, 'GMAPS-service' : record['GMAPS_Listing'], 
                                    'query': record['query'], 'company_name': record['name'], 'company_url': record['website'], 'address': record['address'], 
                                    'email': record['email'], 'phone': record['phone_number']})
        except Exception as e:
            print(e)
            logging.info(e)

    def run(self, queue):
        while True:
            try:
                record = queue.get(block=False)
                self.process(record)
                queue.task_done()  
            except:
                if self.event.is_set():
                    return     
            