#######################
# These tests actually label tickets
# and as such should not be run automatically
# uncomment desired test, put in secret keys, and run manually
# DONT FORGET TO TAKE KEYS OUT BEFORE COMMITING!!!!!
#######################
from rocket_releaser import release_notes


slack_text = release_notes.release_notes(
    "github key",
    "82a86d4",
    "9253704",
    "slack key",
    "staging",
    "staging",
    "",
    "master",
    "15five",
    "rocket_releaser",
)


print(slack_text)

# DID YOU REMEMBER TO TAKE SECRET KEYS OUT?
