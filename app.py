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
	s= "saatvik"
	return s 

if __name__ == "__main__":
	app.run()
 