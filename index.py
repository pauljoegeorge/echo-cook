import logging
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def launch():
  welcome_msg = render_template('welcome')
  return question(welcome_msg)

#  This function will be used for Lambda handler and is configured as main.lambda_function
def lambda_handler(event, _context):
    return ask.run_aws_lambda(event)

@ask.intent("progressIntent")
def in_progress():
  progress_msg = render_template('progress')
  return statement(progress_msg)


@ask.intent("numberIntent", convert={'num': int })
def random_number(num):
  speak_msg = render_template('random', number = str(num))
  return statement(speak_msg)

@ask.intent("cookIntent", convert={'item': str})
def start_cooking(item):
  cook_msg = render_template('start_cooking', food = item)
  return statement(cook_msg)

# add cooking status here
@ask.intent("cookStatusIntent", convert={'dish': str})
def status_cooking(dish):
  cook_msg = render_template('status_cooking', food = dish)
  return statement(cook_msg)

# check cooking history
@ask.intent("historyIntent")
def cooking_history():
  cook_msg = render_template('history_cooking')
  return statement(cook_msg)

if __name__ == '__main__':
    app.run(debug=True)
