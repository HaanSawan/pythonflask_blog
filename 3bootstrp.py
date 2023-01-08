from flask import Flask,render_template
app= Flask(__name__)

@app.route("/bootstrap")
def Boot():
    return render_template("bootstrap.html")

app.run()