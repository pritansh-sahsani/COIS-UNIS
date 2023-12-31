from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from main.forms import LoginForm, RegistrationForm, EditUserForm, AddUniversityForm
from main.setup import app, db
from main.models import User, Uni, Location, Course
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

@app.route("/add_uni", methods=['GET', 'POST'])
@login_required
def add_uni():
    courses = []
    locations=[]
    courses_query= Course.query.with_entities(Course.name).all()
    locations_query = Location.query.with_entities(Location.city, Location.country).all()

    for course in courses_query:
        courses.append((course.name, course.name))

    for location in locations_query:
        locations.append((location.city+", "+location.country, location.city+", "+location.country))

    form = AddUniversityForm(formdata = request.form, courses=courses, locations=locations)

    if form.validate_on_submit():
        if Uni.query.filter_by(name = form.name.data).first():
            flash('A university with this name has been added eariler.')
            return render_template("add_uni.html", form=form)
        
        if not form.website.data or not form.ib_cutoff.data or not form.requirements.data or len(form.courses.data) == 0 or len(form.location.data) == 0:
            is_draft = True
        else:
            is_draft = form.save_draft.data
        
        if form.ib_cutoff.data:
            if form.ib_cutoff.data.isdigit():
                if int(form.ib_cutoff.data) < 0 or int(form.ib_cutoff.data) > 45:
                    flash('Please enter a valid IB grade for cut off (0 to 45).')
                    return render_template("add_uni.html", form=form)
            else:
                flash('Please enter a valid IB grade.')
                return render_template("add_uni.html", form=form)
        else:
            form.ib_cutoff.data = 0

        f = request.files['logo']
        if f:
            filename = form.name.data + '.' + f.filename.rsplit('.', 1)[1].lower()
            f.save(os.path.join(app.root_path, 'university_logos', filename))
        else:
            filename = None
            is_draft = True

        uni = Uni(name = form.name.data, logo = filename, website= form.website.data, ib_cutoff=form.ib_cutoff.data, scholarships=form.scholarships.data, requirements=form.requirements.data, is_draft=is_draft)
        
        for course_name in form.courses.data:
            course = Course.query.filter_by(name=course_name).first()
            uni.courses.append(course)
            course.unis.append(uni)
        for location_name in form.location.data:
            name = location_name.split(", ")
            location = Location.query.filter_by(city=name[0], country=name[1]).first()
            uni.locations.append(location)
            location.unis.append(uni)

        db.session.add(uni)
        db.session.commit()

        if is_draft:
            flash("University saved as draft!", 'success')
        else:
            flash("University added successfully!", 'success')

        return redirect(url_for('manage_unis'))

    return render_template("add_uni.html", form=form)


@app.route("/manage_unis", methods=['GET', 'POST'])
@login_required
def manage_unis():
    sort = request.args.get('sort')
    sort_direction = request.args.get('sort_direction')
    keyword = request.args.get('keyword')
    
    if sort is None or sort_direction is None:
        return redirect("/manage_unis?sort=added_at&sort_direction=true")
    if sort not in ['name','ib_cutoff', 'added_at']:
        abort(404)
    if sort_direction == "true":
        sort_direction = True
    elif sort_direction == "false":
        sort_direction = False
    else:
        abort(404)
    
    if keyword is None or keyword == '':
        draft_unis_query = Uni.query.filter_by(is_draft=True).all()
        published_unis_query = Uni.query.filter_by(is_draft=False).all()
    else:
        draft_unis_query = Uni.query.msearch(keyword).filter_by(is_draft=True).all()
        published_unis_query = Uni.query.msearch(keyword).filter_by(is_draft=False).all()


    draft_unis = []
    published_unis = []
    for uni in draft_unis_query:
        draft_unis.append(uni)
    for uni in published_unis_query:
        published_unis.append(uni)

    for category, reverse in [('name', False), ('ib_cutoff', False), ('added_at', True)]:
        if category != sort:
            draft_unis.sort(key=attrgetter(category), reverse=reverse)
            published_unis.sort(key=attrgetter(category), reverse=reverse)

    draft_unis.sort(key=attrgetter(sort), reverse=sort_direction)
    published_unis.sort(key=attrgetter(sort), reverse=sort_direction)
    
    d_unis_len=len(draft_unis_query)
    p_unis_len=len(published_unis_query)
    flash = "University Deleted Successfully!"

    return render_template("manage_unis.html", published_unis = published_unis, draft_unis=draft_unis, d_unis_len=d_unis_len, p_unis_len=p_unis_len, flash=flash)


@app.route('/uni/<string:uni_name>', methods=['GET', 'POST'])
@login_required
def uni(uni_name):
    return render_template("uni.html")


@app.route('/delete_uni/<int:uni_id>', methods=['GET', 'POST'])
@login_required
def delete_uni(uni_id):
    uni = Uni.query.filter_by(id = uni_id).first_or_404()

    courses = uni.courses
    locations = uni.locations
    for course in courses:
        course.unis.remove(uni)
    for location in locations:
        location.unis.remove(uni)

    if uni.logo:
        os.remove(os.path.join(app.root_path, 'university_logos', uni.logo))
    
    db.session.delete(uni)
    db.session.commit()
    return redirect(url_for('manage_unis'))


@app.route('/edit_uni/<string:uni_name>', methods=['GET', 'POST'])
@login_required
def edit_uni(uni_name):
    old_uni = Uni.query.filter_by(name = uni_name).first_or_404()

    courses = []
    locations=[]
    courses_query= Course.query.with_entities(Course.name).all()
    locations_query = Location.query.with_entities(Location.city, Location.country).all()

    for course in courses_query:
        courses.append((course.name, course.name))

    for location in locations_query:
        locations.append((location.city+", "+location.country, location.city+", "+location.country))

    form = AddUniversityForm(obj=old_uni, formdata = request.form, courses=courses, locations=locations)

    if form.validate_on_submit():
        if not form.website.data or not form.ib_cutoff.data or not form.requirements.data or len(form.courses.data) == 0 or len(form.location.data) == 0:
            is_draft = True
        else:
            is_draft = form.save_draft.data
        
        if form.ib_cutoff.data:
            if form.ib_cutoff.data.isdigit():
                if int(form.ib_cutoff.data) < 0 or int(form.ib_cutoff.data) > 45:
                    flash('Please enter a valid IB grade for cut off (0 to 45).')
                    return render_template("add_uni.html", form=form)
            else:
                flash('Please enter a valid IB grade.')
                return render_template("add_uni.html", form=form)
        else:
            form.ib_cutoff.data = 0

        f = request.files['logo']
        if f:
            filename = form.name.data + '.' + f.filename.rsplit('.', 1)[1].lower()
            f.save(os.path.join(app.root_path, 'university_logos', filename))
        else:
            filename = None
            is_draft = True

        new_uni = Uni(id=old_uni.id, name = form.name.data, logo = filename, website= form.website.data, ib_cutoff=form.ib_cutoff.data, scholarships=form.scholarships.data, requirements=form.requirements.data, is_draft=is_draft)
        db.session.delete(old_uni)
        db.session.add(new_uni)
        
        for course_name in form.courses.data:
            course = Course.query.filter_by(name=course_name).first()
            new_uni.courses.append(course)
            course.unis.append(new_uni)
        for location_name in form.location.data:
            name = location_name.split(", ")
            location = Location.query.filter_by(city=name[0], country=name[1]).first()
            new_uni.locations.append(location)
            location.unis.append(new_uni)

        db.session.commit()

        if is_draft:
            flash("University saved as draft!", 'success')
        else:
            flash("University added successfully!", 'success')

        return redirect(url_for('manage_unis'))

    return render_template("edit_uni.html", form=form, old_uni=old_uni)


@app.route('/add_course/<string:name>')
@login_required
def add_course(name):
    existing = Course.query.filter_by(name = name).first()
    if not existing:
        course = Course(name = name)
        db.session.add(course)
        db.session.commit()
    return redirect(url_for("add_uni"))


@app.route('/add_location/<string:name>')
@login_required
def add_location(name):
    if ',' in name:
        name = name.split(",")
        city=name[0]
        country=name[1]
    else:
        city=name
        country="Unknown"
    
    location=Location(city=city, country=country)
    existing = Location.query.filter_by(city=city, country=country).first()
    if not existing:
        db.session.add(location)
        db.session.commit()
    return redirect(url_for("add_uni"))

@app.route("/manage_users", methods=["GET", "POST"])
@login_required
def manage_users():
    if current_user.username != "SUPERUSER":
        return render_template("403.html")
    
    sort = request.args.get('sort')
    sort_direction = request.args.get('sort_direction')
    keyword = request.args.get('keyword')

    if sort is None or sort_direction is None:
        return redirect("/manage_users?sort=username&sort_direction=false")
    if sort not in ['added_at','email','username']:
        abort(404)
    if sort_direction == "true":
        sort_direction = True
    elif sort_direction == "false":
        sort_direction = False
    else:
        abort(404)
    
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
        
    for category, reverse in [('added_at', True), ('email', False), ('username', False)]:
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
                return redirect(next_page) if next_page else redirect(url_for('manage_unis'))
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
def access_restricted(e):
    return render_template('403.html'), 403