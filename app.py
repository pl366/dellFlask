from flask import Flask , request ,jsonify
from watson_developer_cloud import ToneAnalyzerV3
import simplejson as json
from apscheduler.schedulers.background import BackgroundScheduler
from flask_pymongo import PyMongo
from sklearn.externals import joblib
from bson.objectid import ObjectId
from datetime import datetime,date
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
			if document['reviewSentiment'] is None:
				for x in mongo.db.sentiments.find({}).sort('date',-1):
					docuement['reviewSentiment'] = x['reviewSentiment']
					break  
			if document['serviceFeedbackSentiment'] is None: 
				for x in mongo.db.sentiments.find({}).sort('date',-1):
					document['reviewSentiment'] = x['averageComplaintSentiment']
					break 

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


def sense2():
	print("Scheduler2 is alive!")

	mycol7 = mongo.db.customermls
	# print (mycol ,"mycol")
	# myquery = { "isAltered": "true" }

	mydoc7 = mycol7.find({})
	# print (mydoc,"<-mydoc")
	s1 = 0
	s2 = 0
	s3 = 0
	c = 0
	for document in mydoc7:
		c+=1
		s1+=(document["reviewSentiment"])
		s2+=(document["serviceFeedbackSentiment"])
		s3+=(document["finalSentiment"])
	p1 = round(s1/c,2)
	p2 = round(s2/c,2)
	p3 = round(s3/c,2)	
	post = {"averageComplaintSentiment":p2 ,"averageReview":p1,"averageSentiment":p3 ,"date": datetime.now()}
	posts = mongo.db.sentiments
	posts.insert_one(post)
	return "saatvik and pulkit here , hello "

sched = BackgroundScheduler(daemon=True)
sched.add_job(sense2,'interval',hours=24)
sched.start()



@app.route('/')
@cross_origin()
def hello_world():
	return "Saatvik pulkit are best "

@app.route('/ibm')
# @cross_origin()
# def ibm_score(**kwargs):
# 	@app.route('/ibm')
@cross_origin()
def ibm_score(**kwargs):
	tone_analyzer = ToneAnalyzerV3(
	version='2017-09-21',
	username="27edc35f-d026-4dd3-930e-bac1f6fe10ef",
	password="FmEiqWUBJmDN")

	data = request.args 

	reviewCount = int(data['reviewCount'])

	
	try :
		prevReviewScore = float(data['prevReviewScore'])
	except :
		prevReviewScore = 0 
	text = data['reviewText'] 

	tone_analysis = tone_analyzer.tone({'text': text},'application/json')
	j = json.dumps(tone_analysis, indent=2)
	d = json.loads(j)
	print (d)

	intent = {"Anger":2,"Joy":5,"Sadness":3,"Fear":3,"Confident":4,"Tentative":2,"Analytical":3}

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


@app.route('/customerSurvey',methods=['POST','GET'])
@cross_origin()
def survey(**kwargs):
	if request.method == 'GET':
		return "send post request only yours truly - pulkit and saatvik"

	if request.method == 'POST':
		# print(data['username']) 
		print(request.form["username"])
		data = request.form 

		print(data['username'])
		q1=int(data['level of services you received'])

		print(q1)
		q2=int(data['satisfied with how your problem was dealt'])
		q3=int(data['demeanour of the customer service employee'])
		q4=int(data['employee to be very well informed'])
		q5=int(data['wait for my query acceptable'] )
		te=data['Feedback'] 

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

		intent = {"Anger":2,"Joy":5,"Sadness":3,"Fear":3,"Confident":4,"Tentative":2,"Analytical":3}

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
		username = str(data['username'])
		username = str(username.encode("ascii"))
		# print(type (userstring))
		# # username = "saatvik"
		# print(userstring)
		# for post in mongo.db.customermls.find({"username":{"$in": [d['username']]}}):
		print (mongo.db.customermls.find({"username":{"$in": [username]}}),"uogogg")
		
		for x in mongo.db.customermls.find({"username":{"$in":[username]}}):
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


@app.route('/complaintsX',methods=['GET'])
@cross_origin()
def complaintAverage(**kwargs):
	#sample = [['22-08-2018','13'] ,['24-08-2018' , '8']]

	# todo : score from db is an average , compute average first . this has to be done in the schedular .
	#schedular : computes average evrynight  and  puts it in the required collection , can be done in one collection . 
	# k = [] 
	# j = {} 
	# while :

	# 	j[date] = output of db 
	# 	j[score] = score from db 
	# 	k.append(j)

	k = [] 
	
	mycol4 = mongo.db.sentiments
	mydoc4 = mycol4.find({})


	i=0 

	for x in mongo.db.sentiments.find({}).sort('date',-1):
		j = {} 
		print(x)
		print(x['date'])
		if i>6:
			break
		j["date"] = x['date']
		j["score"] = x['averageComplaintSentiment']
		k.append(j) 
		i+=1




	# sample = [{"date":"22-08-2018" , "score" : "3.8"},{"date":"22-08-2018" , "score" : "3.8"}]
	# response = jsonify({"data":str(sample)})
	response = jsonify(k) 
	response.status_code = 200

	print(k ,"K is ")

	return response

@app.route('/reviewX',methods=['GET'])
@cross_origin()
def reviewAverage(**kwargs):

	k = [] 
	j = {} 

	i=0 

	for x in mongo.db.sentiments.find({}).sort('date',-1):
		j = {} 
		if i>6:
			break
		j["date"] = x['date']
		j["score"] = x['averageReview']
		k.append(j)
		i+=1 



		
	# sample = [{"date":"22-08-2018" , "score" : "3.8"},{"date":"22-08-2018" , "score" : "3.8"}]
	# response = jsonify({"data":str(sample)})
	response = jsonify(k) 
	response.status_code = 200


	return response

@app.route('/sentimentX',methods=['GET'])
@cross_origin()
def sentimentAverage(**kwargs):

	k = [] 
	mycol6 = mongo.db.sentiments
	mydoc6 = mycol6.find({})

	i=0 



	for x in mongo.db.sentiments.find({}).sort('date',-1):
		j = {} 
		if i>6:
			break
		j["date"] = x['date']
		j["score"] = x['averageSentiment']
		k.append(j)
		i+=1  



		
# 	# sample = [{"date":"22-08-2018" , "score" : "3.8"},{"date":"22-08-2018" , "score" : "3.8"}]
# 	# response = jsonify({"data":str(sample)})
	response = jsonify(k) 
	response.status_code = 200

	
	return response


@app.route('/productViewed',methods=['GET'])
@cross_origin()
def productViewed(**kwargs):
	mycol5 = mongo.db.customermls
	mydoc5 = mycol5.find({})
	l1 = 0
	l2 = 0
	l3 = 0
	for x in mydoc5:
		l1+=x['c1']
		l2+=x['c2']
		l3+=x['c3']
	k = [{"l1":l1},{"l1":l2},{"l1":l3}]

	response = jsonify(k) 
	response.status_code = 200

	print(k ,"K is ")

	return response

@app.route('/productBought',methods=['GET'])
@cross_origin()
def productBought(**kwargs):
	mycol5 = mongo.db.customermls
	mydoc5 = mycol5.find({})

	l1 = 0
	l2 = 0
	l3 = 0
	
	for x in mydoc5:
		l1+=x['p1']
		l2+=x['p2']
		l3+=x['p3']

	k = [{"l1":l1},{"l1":l2},{"l1":l3}]
	response = jsonify(k) 
	response.status_code = 200

	print(k ,"K is ")

	return response	

if __name__ == "__main__":
	app.run()
