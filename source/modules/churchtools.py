import requests
import logging
import json
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class churchtools:
 
  def __init__(
      self,
      CT_URL,
      CT_API_PAGE_LIMIT,
      CT_HEADERS_JSON,
      CT_HEADERS_FORM,
      ):
    self.CT_URL = CT_URL
    self.CT_API_PAGE_LIMIT = CT_API_PAGE_LIMIT
    self.CT_HEADERS_JSON = CT_HEADERS_JSON
    self.CT_HEADERS_FORM = CT_HEADERS_FORM
 

  # def ct_get_events(self, date_from, date_to, calendar) -> list:


  def ct_get_calendars(self):

    # --- Get a calendars

    try:
      (result:= requests.get(url = f"{self.CT_URL}/calendars", headers = self.CT_HEADERS_JSON)).raise_for_status()
      result_json = json.loads(result.text)
      result_json_complete = [
        result.status_code,
        result_json["data"]
      ]
      return result_json_complete
    except requests.exceptions.HTTPError as err:
      logger.error(err)
      logger.error(result.text)
      return [f"{result.status_code}:  {result.reason}", False]



  def ct_get_events(self, date_start, date_end):

    # --- Get a events from date to date

    try:
      (result:= requests.get(url = f"{self.CT_URL}/events?from={date_start}&to={date_end}", headers = self.CT_HEADERS_JSON)).raise_for_status()
      result_json = json.loads(result.text)
      result_json_complete = [
        result.status_code,
        result_json["data"]
      ]
      return result_json_complete
    except requests.exceptions.HTTPError as err:
      logger.error(err)
      logger.error(result.text)
      return [f"{result.status_code}:  {result.reason}", False]


  def ct_get_agenda(self, event_id):

    # --- Get a agenda of an event by event_id

    try:
      (result:= requests.get(url = f"{self.CT_URL}/events/{event_id}/agenda", headers = self.CT_HEADERS_JSON)).raise_for_status()
      result_json = json.loads(result.text)
      result_json_complete = [
        result.status_code,
        result_json["data"]
      ]
      return result_json_complete
    except requests.exceptions.HTTPError as err:
      logger.error(err)
      logger.error(result.text)
      return [f"{result.status_code}:  {result.reason}", False]


  def ct_get_song_file_element(self, arrangement_id):
    
    # --- Check for existing arrangement file

    # Create requets session (workaround for requets module due to non standard "files[]" key in POST)
    ct_session = requests.sessions.Session()
    ct_session.get(f"{self.CT_URL}/whoami", headers=self.CT_HEADERS_JSON)

    # Get CSRF token and add to new header
    csrf_token_response = ct_session.get(f"{self.CT_URL}/csrftoken", headers=self.CT_HEADERS_FORM)
    headers = dict(ct_session.headers)
    headers.update({"CSRF-Token": json.loads(csrf_token_response.text)["data"]})

    try:
      (result:= ct_session.get(url = f"{self.CT_URL}/files/song_arrangement/{arrangement_id}", headers = headers)).raise_for_status()
      result_json = json.loads(result.text)
      result_json_complete = [
        result.status_code,
        result_json["data"]
      ]
      return result_json_complete
    except requests.exceptions.HTTPError as err:
      logger.error(err)
      logger.error(result.text)
      return [f"{result.status_code}:  {result.reason}", False]
    finally:
      ct_session.close()


  def ct_get_event(self, event_id) -> json:
  
    # --- Get a agenda of an event by event_id

    try:
      (result:= requests.get(url = f"{self.CT_URL}/events/{event_id}", headers = self.CT_HEADERS_JSON)).raise_for_status()
      result_json = json.loads(result.text)
      result_json_complete = [
        result.status_code,
        result_json["data"]
      ]
      return result_json_complete
    except requests.exceptions.HTTPError as err:
      logger.error(err)
      logger.error(result.text)
      return [f"{result.status_code}:  {result.reason}", False]


  def ct_download_file(self, fileName, fileUrl, target_path):

    try:
      (result:= requests.get(url = fileUrl, headers=self.CT_HEADERS_JSON)).raise_for_status()
      if fileName.split('.')[-1] == 'sng':
        with open(f"{target_path}/{fileName}", 'wb') as file:
          file.write(result.content)
      else:
        with open(f"{target_path}/{fileName}", 'wb') as file:
                  file.write(result.content)
      return True
    except requests.exceptions.HTTPError as err:
      logger.error(err)
      logger.error(result.text)
