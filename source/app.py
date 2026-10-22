from flask import Flask, render_template, request, send_file
import logging
import modules.churchtools as churchtools
import modules.songbeamer as songbeamer
import datetime
import shutil
import os

LOGLEVEL = os.environ.get("LOGLEVEL") or "INFO"

logging.basicConfig(level=LOGLEVEL, format='%(asctime)s-%(levelname)s - %(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger(__name__)

CT_API_PAGE_LIMIT = 100
TMP_FOLDER = "tmp"
SB_ZIP_NAME = "Songbeamer_Paket.zip"
SB_ZIP_EXTRACTION_PATH = 'C:\\temp\\sb'

app = Flask(__name__)

@app.route("/", methods=['get','post'])
def main():

  env_data = request.form

  logger.debug("Checking token and instance")

  if 'token' in env_data and "instance" in env_data:

    if env_data['token'] != "" and env_data["instance"] != "":

      logger.info("Token and instance found")

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
      event_selected = None

      logger.info("Getting calendars")
      # Get calendar names to use them later to query the events associated with the right calendar
      if (calendars_json := ct.ct_get_calendars())[1] == False:
        logger.error("Error during loading calendars: " + str(calendars_json[0]))
        return render_template('home.html', env_data=env_data, error=f"Fehler beim Laden der Kalender: {calendars_json[0]}")
      
      for calendar in calendars_json[1]:
        calendar_names.append(calendar['name'])

      # Sort calendar names alphabetically
      calendar_names.sort()

      date_now_datetime = datetime.datetime.now()
      if 'date_start' in env_data:
        date_start = env_data['date_start']
        logger.info(f"Start date was set to {date_start}")
      else:
        date_start = date_now_datetime.strftime("%Y-%m-%d")

      if 'calendar_selected' in env_data:

        logger.info(f"Calendar was set to {env_data['calendar_selected']}")

        # Get todays date and the one in 2 weeks
        date_later = datetime.datetime.fromisoformat(date_start) + datetime.timedelta(days=1)
        date_end = date_later.strftime("%Y-%m-%d")

        logger.info(f"Querying events")
        # Get events of selected calendar
        if (events := ct.ct_get_events(date_start=date_start, date_end=date_end))[1] == False:
          logger.error("Error during loading events: " + str(events[0]))
          return render_template('home.html', env_data=env_data, error=f"Fehler beim Laden der Events: {events[0]}")


        for event in events[1]:
          if event['calendar']['title'] == env_data['calendar_selected']:
            events_calendar.append(event)

        if 'event_selected' in env_data:

          logger.info(f"Selected event: {env_data['event_selected']}")
          # Get single event object
          if (event_selected_object := ct.ct_get_event(event_id=env_data['event_selected']))[1] == False:
            logger.error("Error during loading the event: " + str(event_selected_object[0]))
            return render_template('home.html', env_data=env_data, error=f"Fehler beim Laden des Events: {event_selected_object[0]}")

          event_selected = event_selected_object[1]

          # Get event agenda
          logger.info(f"Querying agenda")
          if (agenda := ct.ct_get_agenda(event_id=env_data['event_selected']))[1] == False:
            logger.error("Error during loading the event: " + str(agenda[0]))
            return render_template('home.html', env_data=env_data, error=f"Fehler beim Laden des Events: {agenda[0]}")

          if agenda != None:

            agenda_items = agenda[1]['items']

            if 'download_sb' in env_data:

              logger.debug("Cleaning up...")
              if os.path.exists(TMP_FOLDER):
                shutil.rmtree(TMP_FOLDER)
              logger.debug("Creating TMP folder")
              os.makedirs(TMP_FOLDER, exist_ok=True)

              # Extend agenda by attachments if existing
              logger.debug(f"Adding possible attachments to agenda object")
              if len(event['eventFiles']) > 0:
                agenda_items.append({
                  "title": "Anhänge",
                  "type": "header_attachment"
                })
                for attachment in event['eventFiles']:
                  # If attachment is a file
                  agenda_element = {}
                  if attachment['domainType'] == "file":
                    ct.ct_download_file(fileName=attachment['title'], fileUrl=attachment['frontendUrl'], target_path=TMP_FOLDER)
                    agenda_element = {
                      "title": attachment['title'],
                      "type" : attachment['domainType'],
                      "fileName": f"{SB_ZIP_EXTRACTION_PATH}\\{attachment['title']}"
                    }
                    # If attachment is a link
                  if attachment['domainType'] == "link":
                    agenda_element = {
                      "title": attachment['title'],
                      "type" : attachment['domainType'],
                      "fileName": attachment['frontendUrl']
                    }
                  agenda_items.append(agenda_element)

              # Get files for event
              logger.info(f"Collecting files for event")
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
                    
                    if (file_element := ct.ct_get_song_file_element(arrangement_id=item['song']['arrangementId']))[1] == False:
                      logger.error("Error during loading the file element: " + str(file_element[0]))
                      return render_template('home.html', env_data=env_data, error=f"Fehler beim Laden des Dateielementes: {file_element[0]}")
                    
                    fileUrl = file_element[1][0]['fileUrl']
                    ct.ct_download_file(fileName=file_element[1][0]['name'], fileUrl=fileUrl, target_path=TMP_FOLDER)
                    # Check if Song title is not set and replace with file name
                    if item['title'] == "Lied" or item['title'] == "":
                      item['title'] = file_element[1][0]['name'].split('.')[0]
                    agenda_element = {
                      "title": item['title'],
                      "type": item['type'],
                      "fileName": f"{SB_ZIP_EXTRACTION_PATH}\\{file_element[1][0]['name']}",
                      "note": item['note']
                    }
                  case _:
                    agenda_element = item
                agenda_array.append(agenda_element)


              logger.info(f"Creating zip file for SongBeamer")
              # Parse SB collection template
              sb = songbeamer.songbeamer()
              sb.sb_render_template(agenda=agenda_array, target_path=TMP_FOLDER)
              sb.zip_file(path=f"{TMP_FOLDER}/", fileName=SB_ZIP_NAME)

              logger.debug("Cleaning up...")
              if os.path.exists(TMP_FOLDER):
                shutil.rmtree(TMP_FOLDER)

              logger.info(f"Downloading zip file")
              return send_file(SB_ZIP_NAME, as_attachment=True)


      return render_template(
        'home.html',
        env_data=env_data,
        calendar_names=calendar_names,
        events_calendar=events_calendar,
        agenda_items=agenda_items,
        event=event_selected,
        date_start=date_start
      )

    else:

      return render_template('home.html', env_data=env_data, error="Keine Instanz oder Token angegeben")

  else:

    return render_template('home.html', env_data=env_data, error="Keine Instanz oder Token angegeben")


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)