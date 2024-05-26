#!/usr/bin/env python

import sys
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant, skilled in explaining everything in simple terms even an 8 year old can understand."},
    {"role": "user", "content": sys.argv[1]}
  ]
)

print(completion.choices[0].message.content)
