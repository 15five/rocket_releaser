#######################
# These tests actually label tickets
# and as such should not be run automatically
# uncomment desired test, put in secret keys, and run manually
# DONT FORGET TO TAKE KEYS OUT BEFORE COMMITING!!!!!
#######################
from rocketReleaser import release_notes


slack_text = release_notes.release_notes(
    'github key', 'jira key',
    '674913b6cf8f49308e61c90c6f110588d521990c', '950a00d8465ec257cb0ffac56e601ae6bf9a6106',
    'slack key', 'staging', 'staging', "/home/caleb/Documents/fifteen5", 'staging'
)


print(slack_text)

# DID YOU REMEMBER TO TAKE SECRET KEYS OUT?
