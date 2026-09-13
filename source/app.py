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
      
      print(env_data['event_selected'])

      if 'event_selected' in env_data:
        # Get event agenda
        agenda_items = ct.ct_get_agenda(event_id=env_data['event_selected'])['items']

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