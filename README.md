# churchtools_sb_downloader

This webapp shows all ChurchTools events of one nay and the corresponding agenda. The agenda, together with the sond giles and attachments, can be downloaded as zip file for SongBeamer.

The `local_commands.bat` helpfs with extracting the files. They must bgo to `C:\temp\sb`. This is because SonngBeamer does not (yet) support relative file paths in the `*.col` file. If you want to have some other path, do a search & replace in the code.

### Prerequisites

Requirements: Python 3

Set up a python virtual environment in this folder and activate it

```bash
python3 -m venv venv
source venv/bin/activate
```

Install missing modules

```bash
pip install -r requirements.txt
```

### Run the script

Optionally st the log level (defaults to INFO):

```bash
export LOGLEVEL=DEBUG
```

You can run the script just like this:

```bash
python3 app.üy