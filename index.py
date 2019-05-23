import logging
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session, context
import requests
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import math

dynamodb = boto3.resource('dynamodb')
client = boto3.client('dynamodb','ap-northeast-1')
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

@ask.intent("cookIntent", convert={'itemone': str})
def start_cooking(itemone):
  current_time = datetime.now()
  start_dt = current_time.strftime("%d/%m/%Y %H:%M:%S")
  daytime = current_time.strftime("%d%m%Y%H%M%S")
  userId = context.System.user.userId
  db = dynamodb.Table('echoCook')

  db.put_item(
     Item={
          'id': daytime,
          'userId': userId,
          'food_item': itemone,
          'start_dt':start_dt,
          'end_dt': 'None',
      }
  )
  cook_msg = render_template('start_cooking', food = itemone)
  return statement(cook_msg)

# @ask.intent("cookStatusIntent", convert={'dish': str})
# def status_cooking(dish):
# 	if dish != None:
# 	  	# cook_msg = render_template('status_cooking', food = dish)
# 	  	# return statement(cook_msg)
# 	  	userId = context.System.user.userId
#         now = datetime.now()
#         current_time = now.strftime("%d/%m/%Y %H:%M:%S")
#         db = dynamodb.Table('echoCook')
#         response = db.scan(
#             FilterExpression=Attr('userId').eq(userId) and Attr('food_item').eq(dish) and Attr('end_dt').eq('None')
# 	  	)
#         items = response['Items']
#         start_dt = ''
#         hours = ''
#         minutes = ''
#         seconds = ''
# 	   	for item in response['Items']:
# 	   		if str(item['food_item']) == dish: 
# 	   			start_dt = item['start_dt']
# 	   	time_taken = ''
# 	   	if start_dt != '':
# 	   		print("start date ....................."+  str(datetime.strptime(current_time, "%d/%m/%Y %H:%M:%S")))
# 	   		print("end date ....................." + str(datetime.strptime(start_dt, "%d/%m/%Y %H:%M:%S")))
# 	   		total_time = datetime.strptime(current_time, "%d/%m/%Y %H:%M:%S") - datetime.strptime(start_dt, "%d/%m/%Y %H:%M:%S")
# 	   		time_taken = divmod(total_time.days * 86400 + total_time.seconds, 60)
# 	   	else:
# 	   		msg = render_template('failure')
# 	   		return statement(msg)
# 	   	if len(time_taken) == 3:
# 	   		hours = time_taken[0]
# 	   		minutes = time_taken[1]
# 	   		seconds = time_taken[2]
# 	   		print('printing  date.....', str(hours), str(minutes), str(seconds))
# 	   	else:
# 	   		if(time_taken[0] > 59):
# 	   			hours = round(time_taken[0]/60)
# 	   			minutes = time_taken[0] - (hours * 60)
# 	   			seconds = time_taken[1]
# 	   		else:
# 	   			minutes = time_taken[0]
# 	   			seconds = time_taken[1]
# 	   		print('printing  date.....', str(hours), str(minutes), str(seconds))
# 	   	status_msg = ''
# 	   	if hours != '':
# 	   		status_msg = render_template('recent_cooking_status', item  = dish,  hours = int(hours), minutes = int(minutes), seconds = int(seconds))
# 	   	else:
# 	   		status_msg = render_template('very_recent_cooking_status', item = dish, minutes = int(minutes), seconds = int(seconds))
# 	   	return statement(status_msg)
# 	else:
# 		msg = render_template('failure')
#     	return statement(msg)


@ask.intent("finishCookingIntent", convert={'food': str})
def finish_cooking(food):
  if food != None:
    userId = context.System.user.userId
    current_time = datetime.now()
    end_dt = current_time.strftime("%d/%m/%Y %H:%M:%S")
    db = dynamodb.Table('echoCook')
    response = db.scan(
      FilterExpression=Attr('userId').eq(userId) and Attr('food_item').eq(food)
    )
    items = response['Items']
    for item in response['Items']:
      if item['end_dt']=='None':
        print(item['id'],item['food_item'],item['start_dt'])
        db.update_item(
          Key={
            'id': item['id']
          },
          UpdateExpression='SET end_dt = :date',
          ExpressionAttributeValues={
            ':date': end_dt
          }
        )
    end_msg = render_template('end_cooking', food = food)
    return statement(end_msg)
  else:
    end_msg = render_template('end_cooking_error')
    return statement(end_msg)

# @ask.intent("favoriteIntent")
# def favorite():


@ask.intent('AskPermission')
def get_permission():
    # """ Retreive User email from alexa user profile api """
    # token = context.System.apiAccessToken
    # print("token is........." + str(token))
    # api_end_point = context.System.apiEndpoint
    # headers = {
    #     "Host": "api.amazonalexa.com",
    #     "Accept": "application/json",
    #     "Authorization": "Bearer {}".format(token)}
    # body = {
    #           "version": "1.0",
    #           "response": {
    #             "card": {
    #               "type": "AskForPermissionsConsent",
    #               "permissions": [
    #                 "alexa::profile:email:read",
    #               ]
    #             }
    #           }
    #         }

    # resp = requests.get('{api_end_point}/v2/accounts/~current/settings/Profile.email'.format(api_end_point=api_end_point), json=body, headers=headers)
    # if resp.status_code == 200:
    #     print("response is.........." + str(resp.json()))
    #     msg = render_template('success')
    #     return statement(msg)
    # print("response is .........no  .." + str(resp))
    # msg = render_template('failure')
    # return statement(msg)
    uid = context.System.user.userId
    msg = render_template('success', token = uid)
    return statement(msg)

# check cooking history
@ask.intent("historyIntent")
def cooking_history():
	userId = context.System.user.userId
	current_time = now.strftime("%d/%m/%Y %H:%M:%S")
	db = dynamodb.Table('echoCook')
	response = db.scan(
	     FilterExpression=Attr('userId').eq(userId)
	)
	items = response['Items']
	dishes_array = []
	dishes = ''
	for item in items:
		dishes_array.append(items['food_item'])
	if dishes_array != []:
		dishes = ",".join(dishes_array)
		cook_msg = render_template('history_cooking', dishes = dishes)
	else: 		
		cook_msg = render_template('empty_history_cooking')
	return statement(cook_msg)

if __name__ == '__main__':
    app.run(debug=True)
