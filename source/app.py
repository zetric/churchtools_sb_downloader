from flask import Flask, render_template, jsonify, request, send_file
import logging
import modules.churchtools as churchtools
import modules.songbeamer as songbeamer
import datetime
import shutil
import os
import time

logging.basicConfig(level="DEBUG", format='%(asctime)s-%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CT_API_PAGE_LIMIT = 100
TMP_FOLDER = "tmp"
SB_ZIP_NAME = "Songbeamer_Paket.zip"
SB_ZIP_EXTRACTION_PATH = 'C:\\temp\\sb'

app = Flask(__name__)

@app.route("/", methods=['get','post'])
def main():

  env_data = request.form

  if "token" in env_data and "instance" in env_data:

    CT_HEADERS_JSON =  {"Authorization": f"Login {env_data['token']}", "Content-Type": "application/json"}
    CT_HEADERS_FORM =  {"Authorization": f"Login {env_data['token']}", "Content-Type": "multipart/form-data"}

    ct = churchtools.churchtools(
      CT_URL=f"https://{env_data['instance']}/api",
      CT_API_PAGE_LIMIT=CT_API_PAGE_LIMIT,
      CT_HEADERS_JSON=CT_HEADERS_JSON,
      CT_HEADERS_FORM=CT_HEADERS_FORM,
    )
    
    # Early definitions to not let the renering function fail
    calendar_names = []
    events_calendar = []
    agenda_items = []

    # Get calendar names to use them later to query the events associated with the right calendar
    calendars_json = ct.ct_get_calendars()
    for calendar in calendars_json:
      calendar_names.append(calendar['name'])

    # Sort calendar names alphabetically
    calendar_names.sort()

    if 'calendar_selected' in env_data:

      # Get todays date and the one in 2 weeks
      date_now = datetime.datetime.now()
      date_later = date_now + datetime.timedelta(days=14)
      date_start = date_now.strftime("%Y-%m-%d")
      date_end = date_later.strftime("%Y-%m-%d")


      # Get events of selected calendar
      events = ct.ct_get_events(date_start=date_start, date_end=date_end)
      for event in events:
        if event['calendar']['title'] == env_data['calendar_selected']:
          events_calendar.append(event)

      if 'event_selected' in env_data:

        if 'event_selected' in env_data:
          # Get event agenda
          agenda = ct.ct_get_agenda(event_id=env_data['event_selected'])

          if agenda != None:

            agenda_items = agenda['items']

            if 'download' in env_data:

              logger.debug("Cleaning up...")
              if os.path.exists(TMP_FOLDER):
                shutil.rmtree(TMP_FOLDER)
              logger.debug("Creating TMP folder")
              os.makedirs(TMP_FOLDER, exist_ok=True)

              # Get files for event
              agenda_array = []
              for item in agenda_items:
                agenda_element = {}
                match item['type']:
                  case 'text' | 'header':
                    agenda_element = {
                      "title": item['title'],
                      "type": item['type']
                    }
                  case "song":
                    file_element = ct.ct_get_song_file_element(arrangement_id=item['song']['arrangementId'])
                    fileUrl = file_element[0]['fileUrl']
                    ct.ct_download_song_file(fileName=file_element[0]['name'], fileUrl=fileUrl, target_path=TMP_FOLDER)
                    # Check if Song title is not set and replace with file name
                    if item['title'] == "Lied" or item['title'] == "":
                      item['title'] = file_element[0]['name'].split('.')[0]
                    agenda_element = {
                      "title": item['title'],
                      "type": item['type'],
                      "fileName": f"{SB_ZIP_EXTRACTION_PATH}\\{file_element[0]['name']}",
                      "note": item['note']
                    }
                agenda_array.append(agenda_element)

              # DEBUG
              logger.debug(os.listdir("./"))

              # Parse SB collection template
              sb = songbeamer.songbeamer()
              sb.sb_render_template(agenda=agenda_array, target_path=TMP_FOLDER)
              sb.zip_file(path=f"{TMP_FOLDER}/", fileName=SB_ZIP_NAME)

              logger.debug("Cleaning up...")
              if os.path.exists(TMP_FOLDER):
                shutil.rmtree(TMP_FOLDER)

              return send_file(SB_ZIP_NAME, as_attachment=True)

            
        



    return render_template(
      'home.html',
      env_data=env_data,
      calendar_names=calendar_names,
      events_calendar=events_calendar,
      agenda_items=agenda_items
    )



  else:

    return render_template('home.html')


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)