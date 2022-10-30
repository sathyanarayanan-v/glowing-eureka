from cgitb import text
from unittest import result
from flask import Flask, request, render_template
from project import main

app = Flask(__name__)




@app.route("/", methods=['POST','GET'])
def index():
    if request.method=="POST":
        input_string = request.form.get('input_string').strip()
        pattern = request.form.get('pattern').strip()
        results = main(input_string,pattern)
        results["test_run"] = True
        return render_template('index.html',results=results,form=request.form)
    if request.method == "GET":
        return render_template('index.html',results={"duration":-1,"results":None},form=request.form)