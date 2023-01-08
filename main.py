from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime 
import math         #used  at pagination-to take gratest integer


with open("config.json") as f:                  #from jason file
    params=json.load(f)["params"]
local_server= True                      #variable
app= Flask(__name__)
app.secret_key="super-secret-key"

app.config['UPLOAD_FOLDER']= params['upload_location']
app.config.update(                               #using gmail to get email, gmail provide smpt server     
    MAIL_SERVER= 'smtp.gmail.com',
    MAIL_PORT= '465',
    MAIL_USE_SSL= True,
    MAIL_USERNAME= params['email_log'],
    MAIL_PASSWARD= params['email_pass']
    )               
mail= Mail(app)                             #to send mail

if (local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]   #konasa database hai or kaise connect hona hai database se
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["prod_uri"] 
db= SQLAlchemy(app)



class Contacts(db.Model):
# """sno	name	email	ph.num	date	"""
    sno= db.Column(db.Integer, primary_key = True) 
    name= db.Column(db.String(50), nullable=False)      #unique mtlb every name must be unique, that is why i gave false value to it
    email= db.Column(db.String(20), nullable=False) 
    ph_num= db.Column(db.String(14), nullable=False) 
    date= db.Column(db.String(12),nullable=True) 
    msg= db.Column(db.String(120), nullable=False) 


class Posts(db.Model):
# """sno	name	email	ph.num	date	"""
    sno= db.Column(db.Integer, primary_key = True) 
    title= db.Column(db.String(50), nullable=False)      #unique mtlb every name must be unique, that is why i gave false value to it
    slug= db.Column(db.String(50), nullable=False) 
    content= db.Column(db.String(14), nullable=False) 
    date= db.Column(db.String(12),nullable=True) 
    by= db.Column(db.String(120), nullable=False) 
    sub_title= db.Column(db.String(120), nullable=False) 

@app.route("/")
def Index():
    return render_template("index.html",params=params)



@app.route("/home")
def Home():
    posts=Posts.query.filter_by().all()
    #[0:params["no_of_post"]]
    last= math.ceil(len(posts)/int(params["no_of_post"]))    #calculating total no of pages
    #pagination
    #first page---- prev url= blank, next url= page+1
    #middle page---- prev url= page-1, next url= page+1
    #first page---- prev url= page-1, next url= blank
    page=request.args.get("page")                          #getting no of pages
    if page is None:                         #for homep
        page=1
    else:
        page= int(page)
    posts= posts[(page-1) * int(params["no_of_post"]): (page-1)* int(params["no_of_post"])+int(params["no_of_post"])]
    if page==1:
        prev="#"
        next="?page="+str(page+1)
    elif page==last:
        prev="?page="+str(page-1)
        next="#"
    else:
        prev="?page="+str(page-1)
        next="?page="+str(page+1)    
    return render_template("index.html",params=params,posts=posts,prev=prev,next=next)



@app.route("/about")
def About():
    return render_template("about.html",params=params)




@app.route("/edit/<string:sno>", methods = ['GET','POST'])
def edit(sno):
    if "user" in session and session["user"] == params["admin_user"] :
        if request.method == "POST":
            #you can give html and python variable differnt name(like here i can use box_titt or any name which may be diff from name in html)
            box_title = request.form.get("title")
            box_slug = request.form.get("slug")
            box_content = request.form.get("content")
            box_subtitle = request.form.get("sub_title")
            box_by = request.form.get("by")
            date=datetime.now()
            
            #we are checking here if sno is 0 ie we are writting new post, if sno is 1,2 or any that mean we are editing the post
            if sno == "0":  #to add new
                post = Posts(title=box_title, slug=box_slug, content=box_content, sub_title= box_subtitle, by= box_by,date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()  #to edit the already exist
                post.title= box_title
                post.slug= box_slug
                post.content = box_content
                post.sub_title = box_subtitle
                post.by = box_by
                db.session.commit()
                return redirect('/edit/' +sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template("edit.html",params=params,post=post,sno=sno)


    

@app.route("/login", methods = ['GET','POST'])
def login():
    if "user" in session and session["user"] == params["admin_user"] :
        posts=Posts.query.all()                      #to fetch all post from database
        return render_template("dashboard.html",params=params,posts=posts)

    if (request.method=='POST'):    
        username= request.form.get("uname")
        userpass= request.form.get("pass")
        if (username == params["admin_user"] and userpass == params["admin_pass"] ):
        #set the session variable
             session["user"] = username
             posts=Posts.query.all()
             return render_template("dashboard.html",params=params,posts=posts)      
    else:     
        return render_template("login.html",params=params)




@app.route("/dashboard")
def dashboard():
    if "user" in session and session['user']==params['admin_user']:
        posts = Posts.query.all()
        return render_template("dashboard.html", params=params, posts=posts)

    if request.method=="POST":
        username = request.form.get("uname")
        userpass = request.form.get("upass")
        if username==params['admin_user'] and userpass==params['admin_password']:
            # set the session variable
            session['user']=username
            posts = Posts.query.all()
            return render_template("dashboard.html", params=params, posts=posts)
    else:
        return render_template("login.html", params=params)




@app.route("/contact", methods = ['GET','POST'])                  #post request in flask
def Contact():
    if (request.method=='POST'):                            #importing request module         
        '''add entry to database'''
        name= request.form.get("name")
        email= request.form.get("email")
        phone= request.form.get("phone")
        message= request.form.get("message")
        
        entry = Contacts(name= name, email=email, ph_num=phone,date= datetime.now(), msg=message)

        # entry= Contacts ( name=request.form.get("name"),             #alternative
        #                 email=request.form.get("email"),
        #                 ph_num=request.form.get("phone"),
        #                 msg=request.form.get("message") )
 #sno name email ph_num date
        db.session.add(entry)
        db.session.commit()
        mail.send_message("new message from " +name,                 #to send mail in our contact page
                          sender=email,
                          recipients=[params['email_log']],
                          body=message + "\n" + phone
                           )
    return render_template("contact.html",params=params)


        

@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post= Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",params=params,post=post)




@app.route("/uploader", methods = ['GET','POST'])
def uploader():
    if "user" in session and session['user']==params['admin_user']:
        if (request.method=="POST"):
            f= request.files["file1"]            
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))            
            return redirect("/dashboard")


        

@app.route("/logout")
def logout():
    session.pop("user")   # to kill the session
    return redirect("/dashboard")

    s

@app.route("/delete/<string:sno>", methods = ['GET','POST'])
def delete(sno):
    if "user" in session and session ["user"]== params["admin_user"]:
        post= Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect("/dashboard")




app.run(debug=True)