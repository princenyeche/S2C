from configparser import ConfigParser, ExtendedInterpolation
from jiraone import LOGIN, PROJECT, file_reader, add_log, endpoint, echo


config = ConfigParser(interpolation=ExtendedInterpolation())
config.read("config.ini")

# Create a JQL that can extract from multiple projects (if any), don't worry we'll handle any size
# This will work if and only if the source and target project keys are the same else you'll receive a 404 not found.
jql = "project in (COM) ORDER BY Rank DESC"  # define any valid JQL to search for project that has attachments

# server config
user = config["server"]["username"]
password = config["server"]["password"]
link = config["source"]["instance"]
LOGIN.api = False
LOGIN(user=user, password=password, url=link)
check = LOGIN.get(endpoint.myself())

# folder and file config
folders = "Attachments"
file_names = "attachment_data.csv"


def begin(init: bool = True):

    if init is True:
        # source config
        LOGIN(user=user, password=password, url=link)
        PROJECT.get_attachments_on_projects(attachment_folder=folders,
                                            attachment_file_name=file_names,
                                            query=jql)

        print("Attachment from {} downloaded".format(config["source"]["instance"]))
        print("*" * 120)

    if init is False:
        # target config
        ta_users = config["cloud"]["email"]
        ta_password = config["cloud"]["token"]
        ta_links = config["target"]["instance"]
        LOGIN(user=ta_users, password=ta_password, url=ta_links)
        look = LOGIN.get(endpoint.myself())
        
        if look.status_code == 200:
            def load_attach(last_cell=True):
                read = file_reader(folder=folders, file_name=file_names, skip=True)
                add_log("Reading attachment {}".format(file_names), "info")
                count = 0
                cols = read
                length = len(cols)
                for r in read:
                    count += 1
                    keys = r[3]
                    attachment = r[8]
                    _file_name = r[6]
                    LOGIN(user=user, password=password, url=link)
                    fetch = LOGIN.get(attachment).content
                    # use the files keyword args to send multipart/form-data in the post request of LOGIN.post
                    payload = {"file": (_file_name, fetch)}
                    # modified our initial headers to accept X-Atlassian-Token to avoid (CSRF/XSRF)
                    new_headers = {"Accept": "application/json",
                                   "X-Atlassian-Token": "no-check"}
                    # we're using two different authentications. so we need to call them separately.
                    LOGIN(user=ta_users, password=ta_password, url=ta_links)
                    LOGIN.headers = new_headers
                    run = LOGIN.post(endpoint.issue_attachments(keys, query="attachments"), files=payload)
                    if run.status_code != 200:
                        print("Attachment not added to {}".format(keys), "Status code: {}".format(run.status_code))
                        add_log("Attachment not added to {} due to {}".format(keys, run.reason), "error")
                    else:
                        print("Attachment added to {}".format(keys), "Status code: {}".format(run.status_code))
                        add_log("Attachment added to {}".format(keys), "info")
                    # remove the last column since it contains an empty cells.
                    if last_cell is True:
                        if count >= (length - 1):
                            break

            load_attach(last_cell=True)

            print("Attachments copied to {}".format(config["target"]["instance"]))
        else:
            echo("Please check your cloud credentials, as it might be wrong...")
            

if __name__ == "__main__":
    if check.status_code == 200:
        begin()
        print("Copying attachments...")
        begin(False)
    else:
        echo("Please check your server credentials, as it might be wrong...")
