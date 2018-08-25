from flask import Flask , request ,jsonify
from watson_developer_cloud import ToneAnalyzerV3
import simplejson as json
from apscheduler.schedulers.background import BackgroundScheduler
from flask_pymongo import PyMongo
from sklearn.externals import joblib
from bson.objectid import ObjectId



app = Flask(__name__)
 


app.config['MONGO_DBNAME'] = 'dellprod'
app.config['MONGO_URI'] = 'mongodb://umaniax:hello1234@ds125342.mlab.com:25342/dellprod'
          
mongo = PyMongo(app)    

def sensor():
    """ Function for test purposes. """




clf = joblib.load('trained.pkl') 

def sense():
	print("Scheduler is alive!")

	mycol = mongo.db.customermls
	# print (mycol ,"mycol")
	myquery = { "isAltered": "true" }

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
def hello_world():
	return "Saatvik pulkit are best "


@app.route('/ibm')
def ibm_score(**kwargs):
	tone_analyzer = ToneAnalyzerV3(
	version='2017-09-21',
	username="27edc35f-d026-4dd3-930e-bac1f6fe10ef",
	password="FmEiqWUBJmDN")

	data = request.args 

	reviewCount = int(data['reviewCount'])

	prevReviewScore = int(data['prevReviewScore'])

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

if __name__ == "__main__":
	app.run()
 