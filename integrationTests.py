#######################
# These tests actually label tickets
# and as such should not be run automatically
# uncomment desired test, put in secret keys, and run manually
# DONT FORGET TO TAKE KEYS OUT BEFORE COMMITING!!!!!
#######################
from rocket_releaser import release_notes


slack_text = release_notes.release_notes(
    "***REMOVED***",
    "73e006e",
    "dd10ce4",
    "15five",
    "dev",
    "dev",
    "",
    "dev",
    "15five",
    "rocket_releaser",
)


print(slack_text)

# DID YOU REMEMBER TO TAKE SECRET KEYS OUT?
