
from flask import Flask,render_template
app= Flask(__name__)

@app.route("/")
def Hello():
    return render_template("index.html")


@app.route("/term")
def Sawan():
    name ="sawan"
    return render_template("term.html",Name=name)      #Name=name in html and , name= name in py

app.run()
