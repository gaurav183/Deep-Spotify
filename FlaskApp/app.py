from __future__ import print_function # In python 2.7

from flask import Flask, render_template, redirect, url_for, request

import sys
app = Flask(__name__)

from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from search import Search


@app.route("/")
def main():
	return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
	print(request.form['song'], file=sys.stderr)
	search = Search(request.form['song'])
	genres = search.run()
	# make sure 
	print(genres, file=sys.stderr)
	genre1 = genres[0]
	if (len(genres)==2):
		genre2 = genres[1]
	else: 
		genre2 = ''
	print(genres, file=sys.stderr)
	

   	return render_template('result.html', genre1=genre1, genre2=genre2)

if __name__ == "__main__":
  app.run()
