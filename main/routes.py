from flask import render_template, url_for, flash, redirect, request
from flask_login import current_user, login_user, logout_user, login_required
from main.forms import LoginForm, RegistrationForm, ContactForm, MessageReplyForm, EditUserForm
from main.setup import app, db
from main.models import User, Messages, MessageReply
from main import bcrypt
from dotenv import load_dotenv
from operator import attrgetter
import os

load_dotenv()

SUPER_USER_KEY = os.getenv('SUPER_USER_KEY')

@app.route("/", methods=["GET", "POST"])
def index():
    # todo: overview of unis
    return render_template("index.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    contact_form=ContactForm(formdata = request.form)
    if contact_form.validate_on_submit():
        contact=Messages(name=contact_form.name.data, email=contact_form.email.data, message=contact_form.message.data)
        db.session.add(contact)
        db.session.commit()
        flash('Message sent successfully! We will respond shorty by mail!', 'success')

        return redirect(url_for('index'))
    return render_template("contact.html", contact_form=contact_form)


@app.route("/manage_users", methods=["GET", "POST"])
# @login_required
def manage_users():
    # if current_user.username != "SUPERUSER":
    #     return render_template("403.html")

    sort = request.args.get('sort') if request.args.get('sort')!=None else None
    sort_direction = request.args.get('sort_direction')
    keyword = request.args.get('keyword')
    
    if sort is None or sort_direction is None:
        return redirect("/manage_users?sort=username&sort_direction=false")

    if sort_direction == "true":
        sort_direction = True
    elif sort_direction == "false":
        sort_direction = False
    else:
        sort_direction = None
    
    if keyword is None or keyword=='':
        user_query = User.query.all()
    else:
        split = keyword.find('-')
        if not split<0:
            keyword = keyword[:split]
        user_query = User.query.msearch(keyword).all()
    
    users = []
    for user in user_query:
        if user.username != "SUPERUSER":
            users.append(user)
    
    if len(users) == 0:
        return render_template("manage_users.html", users=users)
        
    for category, reverse in [('created_at', True), ('email', False), ('username', False)]:
        if category != sort:
            users.sort(key=attrgetter(category), reverse=reverse)
    users.sort(key=attrgetter(sort), reverse=sort_direction)
    
    del_flash = "User Deleted successfully!"
    return render_template("manage_users.html", del_flash=del_flash, users=users)
    
@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id = user_id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('view_users'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    old_user = User.query.filter_by(id = user_id).first_or_404()
    form = EditUserForm(formdata = request.form)

    if form.validate_on_submit():
        if form.super_user_key.data != SUPER_USER_KEY:
            flash('Incorrect Super User Key.', 'danger')

        else:
            User.query.filter_by(id=old_user.id).update(dict(email=form.email.data, username=form.username.data))

            if form.password.data !="":
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                User.query.filter_by(id=old_user.id).update(dict(password=hashed_password))
            db.session.commit()

            flash(f'User data updated successfully!', 'success')
            return redirect(url_for('manage_users'))

    return render_template('edit_user.html', form=form, old_user=old_user)


@app.route("/messages")
@login_required
def view_messages():
    sort = request.args.get('sort') if request.args.get('sort')!=None else None
    sort_direction = request.args.get('sort_direction')
    keyword = request.args.get('keyword')

    if sort_direction == "true":
        sort_direction = True
    elif sort_direction == "false":
        sort_direction = False
    else:
        sort_direction = None
    
    if sort is None or sort_direction is None:
        return redirect("/messages?sort=read&sort_direction=false")
    
    if keyword is None or keyword=='':
        message_query = Messages.query.all()
    else:
        message_query = Messages.query.msearch(keyword).all()
    reply_query = MessageReply.query.all()
    
    messages = []
    replies = {}
    for message in message_query:
        messages.append(message)
    for reply in reply_query:
        replies[reply.message_id] = reply.reply
    
    if len(messages) == 0:
        return render_template("messages.html", no_msg=True)
    else:
        for category, reverse in [('created_at', True), ('replied', False), ('read', False)]:
            if category != sort:
                messages.sort(key=attrgetter(category), reverse=reverse)
                
        messages.sort(key=attrgetter(sort), reverse=sort_direction)
        
        read_flash = 'Message Marked As Read Successfully!'
        unread_flash = 'Message Marked As Unread Successfully!'
        del_flash = "Message Deleted successfully!"

        return render_template("messages.html", no_msg=False, del_flash=del_flash, read_flash=read_flash, unread_flash=unread_flash, messages=messages, replies=replies)
    
@app.route('/delete_message/<int:message_id>', methods=['GET', 'POST'])
@login_required
def delete_message(message_id):
    message = Messages.query.filter_by(id = message_id).first_or_404()
    message_reply = MessageReply.query.filter_by(message_id = message_id).first()
    db.session.delete(message)
    if message_reply is not None:
        db.session.delete(message_reply)
    db.session.commit()
    return redirect(url_for('view_messages'))

@app.route('/read_message/<int:message_id>', methods=['GET', 'POST'])
@login_required
def read_message(message_id):
    message = Messages.query.filter_by(id = message_id).first_or_404()
    Messages.query.filter_by(id = message_id).update(dict(read = (not message.read)))
    db.session.commit()
    return redirect(url_for('view_messages'))

@app.route('/reply_message/<string:message_id>', methods=['GET', 'POST'])
@login_required
def reply_message(message_id):
    message = Messages.query.filter_by(id = message_id).first_or_404()
    # reply if exists
    reply = MessageReply.query.filter_by(message_id = message_id).first()
    reply_form = MessageReplyForm(formdata = request.form)

    if reply_form.validate_on_submit():
        subject = "Reply to your message"
        body = f"""Hello { message.name }!
        I am mailing regarding your message on my blog, The Bland Mirror.
        
        { reply_form.reply.data }"""
        
        # todo: mail setup
        # msg = Message(subject = subject, sender=app.config['MAIL_USERNAME'], body=body, recipients=[message.email])
        # mail.send(msg)

        Messages.query.filter_by(id = message_id).update(dict(replied = True, read = True))
        db.session.commit()
        reply = MessageReply(message_id = message_id, reply=reply_form.reply.data)
        db.session.add(reply)
        db.session.commit()

        flash("Reply Sent Sucessfully!")
        return redirect(url_for('view_messages'))

    return render_template("reply_message.html", reply_form = reply_form, message = message, reply= reply)




@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(formdata = request.form)

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            if user.username != "SUPERUSER":
                return redirect(next_page) if next_page else redirect(url_for('manage_universities'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('manage_users'))
        else:
            flash('Login Unsuccessful, Please Check Your Username And Password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged Out Successfully!")
    return redirect(url_for('index'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm(formdata = request.form)

    if form.validate_on_submit():
        if form.super_user_key.data != SUPER_USER_KEY:
            flash('Incorrect Super User Key.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)

            db.session.add(user)
            db.session.commit()

            flash(f'Your account has been created! You are now able to log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403