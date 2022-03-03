import urllib.request
import re
import json
import subprocess

import os
from dotenv import load_dotenv
load_dotenv()


JSON_PATH = "jasima/data.json"

help_message = "The word you requested, ***{}***, is not in the dictionary. Make sure you didn't misspell it, or talk to õwo úwu (bucketfish#3961) if this word really is missing.\n"
sheets_fail = "Something's wrong, I don't know why this error would even happen. Please tell õwo úwu (bucketfish#3961)."
exception_nonspecific = "Something failed and I'm not sure what. Please tell õwo úwu (bucketfish#3961)."


def read_json():
    with open(JSON_PATH) as f:
        return json.load(f)

def get_word_entry(word):
    bundle = read_json()
    entries = bundle["data"]
    if word not in entries:
        return help_message.format(word)
    return entries[word]
