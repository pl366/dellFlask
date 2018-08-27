from flask import Flask , request ,jsonify
from watson_developer_cloud import ToneAnalyzerV3
import simplejson as json
from apscheduler.schedulers.background import BackgroundScheduler
from flask_pymongo import PyMongo
from sklearn.externals import joblib
from bson.objectid import ObjectId
from datetime import datetime
from flask_cors import CORS, cross_origin



app = Flask(__name__)
 

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGO_DBNAME'] = 'dellprod'
app.config['MONGO_URI'] = 'mongodb://umaniax:hello1234@ds125342.mlab.com:25342/dellprod'
          
mongo = PyMongo(app)    


clf = joblib.load('trained.pkl') 
clf2 = joblib.load('trained2.pkl') 
def sense():
	print("Scheduler is alive!")

	mycol = mongo.db.customermls
	# print (mycol ,"mycol")
	# myquery = { "isAltered": "true" }

	mydoc = mycol.find({})
	# print (mydoc,"<-mydoc")

	sentimentParams = []

	for document in mydoc:
		if document['isAltered']:
			sentimentParams.append([document["c1"],document["c2"],document["c3"],document["p1"],document["p2"],document["p3"],document["reviewSentiment"],document["serviceFeedbackSentiment"]])
			

	l = clf.predict(sentimentParams)

	i =0 
	myd = mycol.find({})
	# print(sentimentParams)
	for docu in myd:
		if docu['isAltered']:
			criteria = docu['_id']
			mongo.db.customermls.update_one({'_id': ObjectId(criteria)},{"$set": {"finalSentiment":l[i] ,"isAltered" : False }})
			i+=1
			print ("\nRecords updated successfully\n") 
		
	print (l)	


	return str(l)

sched = BackgroundScheduler(daemon=True)
sched.add_job(sense,'interval',minutes=1)
sched.start()

@app.route('/')
@cross_origin()
def hello_world():
	return "Saatvik pulkit are best "


@app.route('/ibm')
@cross_origin()
def ibm_score(**kwargs):
	tone_analyzer = ToneAnalyzerV3(
	version='2017-09-21',
	username="27edc35f-d026-4dd3-930e-bac1f6fe10ef",
	password="FmEiqWUBJmDN")

	data = request.args 

	reviewCount = int(data['reviewCount'])

	prevReviewScore = float(data['prevReviewScore'])

	text = data['reviewText'] 

	tone_analysis = tone_analyzer.tone({'text': text},'application/json')
	j = json.dumps(tone_analysis, indent=2)
	d = json.loads(j)
	print (d)

	intent = {"Anger":2,"Joy":5,"Sadness":3,"Fear":4,"Confident":3,"Tentative":1,"Analytical":2}

	i = 0
	s = 0
	count = 0
	while True:
		try:
			s+=(intent[d["document_tone"]["tones"][i]["tone_name"]])*(d["document_tone"]["tones"][i]["score"])
			i+=1
			count+=1
		except:
			if (count!=0):
				s= s/count
			count = 0	
			break	

	finalScore = (s*(reviewCount+1) + prevReviewScore*reviewCount )/(reviewCount * 2 + 1)  

	response = jsonify({'score': str(finalScore)})

	response.status_code = 200
	
	return response

now = datetime.now()
@app.route('/complaints')
@cross_origin()
def complaints_priority(**kwargs):
	mycol2 = mongo.db.complaints
	mydoc2 = mycol2.find({})
	l = []
	for d in mydoc2:
		if d['onGoing']:
			m = d['issuedAt']
			print (d['username'])
			cid = d['complaintId']
			# print (m)
			# print (type(m))
			# print (now)
			p = int(((now - m).total_seconds())//86400)
			print(mongo.db.customermls.find({"username":{"$in": [d['username']]}}))
			for post in mongo.db.customermls.find({"username":{"$in": [d['username']]}}):
				l.append([cid,(post['finalSentiment']+p*0.2)])

	print (l)				
	l.sort(key = lambda x : x[1],reverse = True)
	print (l)	
	response = jsonify({'list': str(l)})
	response.status_code = 200
	
	return response	


@app.route('/customerSurvey')
@cross_origin()
def survey(**kwargs):

	# if request.method == 'GET':
		# print(data['username']) 
		# print("WTFF")
		# print(data['demeanour of the customer service employee'])
	data = request.args 

	print(data['username'])
	q1=int(data['level of services you received'])

	print(q1)
	q2=int(data['satisfied with how your problem was dealt'])
	q3=int(data['demeanour of the customer service employee'])
	q4=int(data['employee to be very well informed'])
	q5=int(data['wait for my query acceptable'] )
	te = data['Feedback'] 

	print(q1,q2,q3,q4,q5,te)

	tone_analyzer = ToneAnalyzerV3(
	version='2017-09-21',
	username="27edc35f-d026-4dd3-930e-bac1f6fe10ef",
	password="FmEiqWUBJmDN")

	print("before printing text" )
	print(data['Feedback'], "<- text")

	text = data['Feedback']

	print(text) 

	tone_analysis = tone_analyzer.tone({'text': text},'application/json')
	j = json.dumps(tone_analysis, indent=2)
	d = json.loads(j)
	print (d)

	intent = {"Anger":2,"Joy":5,"Sadness":3,"Fear":4,"Confident":3,"Tentative":1,"Analytical":2}

	i = 0
	s = 0
	count = 0
	while True:
		try:
			s+=(intent[d["document_tone"]["tones"][i]["tone_name"]])*(d["document_tone"]["tones"][i]["score"])
			i+=1
			count+=1
		except:
			if (count!=0):
				s=s/count
			count = 0	
			break	

	print(s) 

	#todo 1. Machine learning : predict the score given q1 , q2 .. q6

	s = clf2.predict([[q1,q2,q3,q4,q5,s]])

	#todo 2 . Use pymongo and update in db using username as key 

	mycol3 = mongo.db.customermls
	mydoc3 = mycol3.find({})
	print(mydoc3)
	username = data['username']
	# username = "saatvik"
	print(username)
	# for post in mongo.db.customermls.find({"username":{"$in": [d['username']]}}):
	print (mongo.db.customermls.find({"username":{"$in": [username]}}),"uogogg")
	
	for x in mongo.db.customermls.find({"username":{"$in": [username]}}):
		print(x)
		prevCount = x['feedbackCount']
		prevScore = x['serviceFeedbackSentiment']


	finalSen = float((s*(prevCount+1) + prevScore * prevCount) /(2*prevCount + 1 ) )
	newCount = prevCount + 1


	print (finalSen)

	# for doc in mydoc3 :
	# 	if doc['username'] == username :
	# 		print ("oihoihihohoh")
	# 		# mongo.db.customermls.update_one({'_id': ObjectId(criteria)},{"$set": {"finalSentiment":l[i] ,"isAltered" : False }})
	mongo.db.customermls.update_one({'username': username},{"$set": {"serviceFeedbackSentiment":finalSen,"feedbackCount" : newCount  ,"isAltered" : True }})
	return ("\nRecords updated successfully\n")   	

if __name__ == "__main__":
	app.run()
<<<<<<< HEAD

 
=======
 
>>>>>>> 7cc47349ce681dbcd9e54d5431f3696380ead655
