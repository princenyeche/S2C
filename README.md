# ATTACHMENT TRANSFER SCRIPT

* This scripts helps to transfer attachments securely from a Jira server instance to Jira cloud instance

## Config
* A configuration file exist called `config.ini` which houses the server and cloud instance details.
* Only change the fields where the comment mentioned it can be changed.
* Do not change the server or cloud sections.

## Requirement
* This script requires python >= 3.6.x so download the versions higher or equivalent to it to use the script.Preferably use version 3.7.9.
* Install the requirements from the `requirements.txt` file

Check your python version by running
```bash
python -v
```

Before running the below command
```bash
pip install -r requirements.txt
```

## Run
* To start up the script, go to your terminal or command prompt and type
```python
python attachment_transfer.py
```
Assuming that you're already on python 3 the above should work.
