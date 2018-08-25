from flask import Flask
from watson_developer_cloud import ToneAnalyzerV3
app = Flask(__name__)

@app.route('/')
def hello_world():
	return "Hello World"


@app.route('/ibm')
def ibm_score():
	tone_analyzer = ToneAnalyzerV3(
	version='2017-09-21',
	username="27edc35f-d026-4dd3-930e-bac1f6fe10ef",
	password="FmEiqWUBJmDN")

	text = "Fuck your Product"

	tone_analysis = tone_analyzer.tone({'text': text},'application/json')
	j = json.dumps(tone_analysis, indent=2)
	d = json.loads(j)
	print (d)

	intent = {"Anger":2,"Joy":5,"Sadness":3,"Fear":4,"Confident":3,"Tentative":1,"Analytical":2}

	i = 0
	s = 0
	while True:
		try:
			s+=(intent[d["document_tone"]["tones"][i]["tone_name"]])*(d["document_tone"]["tones"][i]["score"])
			i+=1
		except:
			break	

	print (s)	
	return s 

if __name__ == "__main__":
	app.run()
 