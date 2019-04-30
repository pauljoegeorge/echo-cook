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

# @ask.intent("YesIntent")
# def positive_response():
#   jokes = [
# 	" Never trust math teachers who use graph paper. They are always plotting something.",
# 	" What do you get when you cross a snake with a tasty dessert? A pie-thon!",
# 	"Why is Peter Pan flying all the time? He Neverlands!"
# 	]
#   joke = random.choice(jokes)
#   joke_template = render_template('fun', joke=joke)
#   return statement(joke_template)

# @ask.intent("NoIntent")
# def negative_response():
#     response= render_template('no_response')
#     return statement(response)


if __name__ == '__main__':
    app.run(debug=True)
