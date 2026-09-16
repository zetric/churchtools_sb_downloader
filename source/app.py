from flask import Flask, render_template, jsonify, request
import logging
import modules.churchtools as churchtools
import datetime


logging.basicConfig(level="INFO", format='%(asctime)s-%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CT_API_PAGE_LIMIT = 100

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
          agenda_items = ct.ct_get_agenda(event_id=env_data['event_selected'])['items']


          if 'download' in env_data:

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
                  file_element = ct.ct_get_song_file(arrangement_id=item['song']['arrangementId'])
                  file_url = file_element[0]['fileUrl']
                  # TODO: Download file
                  agenda_element = {
                    "title": item['title'],
                    "type": item['type'],
                    "fileName": file_element[0]['name']
                  }
              agenda_array.append(agenda_element)

            print(agenda_array[3])



    return render_template(
      'home.html',
      env_data=env_data,
      calendar_names=calendar_names,
      events_calendar=events_calendar,
      agenda_items=agenda_items
    )



  else:

    return render_template('home.html')

# @app.route("/api/trainings")
# def list_trainings():
#   trainings = load_trainings_from_db()
#   return jsonify(trainings)

# @app.route("/training/<id>")
# def show_training(id):
#   training = load_training_from_db(id)
#   if not training:
#     return "Not Found", 404
#   else:
#     return render_template('trainingpage.html',training=training)

# @app.route("/training/<id>/apply", methods=['post'])
# def apply_to_training(id):
#   data = request.form
#   training = load_training_from_db(id)
#   add_application_to_db(id, data)

  # send an email
  return render_template('application_submitted.html', application=data, training=training)

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)