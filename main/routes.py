from main.forms import LoginForm, AdminRegistrationForm, EditAdminForm, AddUniversityForm, StudentRegistrationForm, EditStudentForm, FilterForm
from main.setup import app, db
from main.models import User, Uni, Location, Course, Student_details
from main.helper import sort_by_similarity, allow_access
from main import bcrypt

from flask import render_template, url_for, flash, redirect, request
from flask_login import current_user, login_user, logout_user, login_required
from dotenv import load_dotenv
import os

load_dotenv()

HASHED_SUPER_USER_KEY = os.getenv('HASHED_SUPER_USER_KEY')

@app.route("/", methods=["GET", "POST"])
def index():
    keyword = request.args.get('keyword')
    unis = Uni.query.filter_by(is_draft=False).all()

    if keyword is not None and keyword != '':
        unis=sort_by_similarity(unis, keyword, column='name')
    
    courses = []
    locations=[]
    courses_query= Course.query.with_entities(Course.name).all()
    locations_query = Location.query.with_entities(Location.exact_location).all()

    for course in courses_query:
        courses.append((course.name, course.name))

    for location in locations_query:
        locations.append((location.exact_location, location.exact_location))

    form = FilterForm(formdata = request.form, courses=courses, locations=locations)

    if form.validate_on_submit():
        if form.submit.data:
            for filter in ['ib_cutoff', 'requirements', 'scholarships']:
                if getattr(form, filter).data!="":
                    unis=sort_by_similarity(unis, getattr(form, filter).data, filter)
            for filter in ['courses', 'location']:
                if len(getattr(form, filter).data)!=0:
                    for item in getattr(form, filter).data:
                        unis=sort_by_similarity(unis, item, filter)

        if form.submit.data:
            for uni in Uni.query.filter_by(is_draft=False).all():
                if not uni in unis:
                    unis.append(uni)
        
    if len(unis) == 0:
        return render_template("index.html", no_unis=True, form=form, courses=courses, locations=locations)

    return render_template("index.html", unis=unis, form=form, courses=courses, locations=locations)

@app.route("/add_uni", methods=['GET', 'POST'])
@login_required
def add_uni():
    if allow_access("admins") is not None: return allow_access("admins")
    courses=[]
    locations=[]
    courses_query= Course.query.with_entities(Course.name).all()
    locations_query = Location.query.with_entities(Location.exact_location).all()

    for course in courses_query:
        courses.append((course.name, course.name))

    for location in locations_query:
        locations.append((location.exact_location, location.exact_location))

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
            location = Location.query.filter_by(exact_location = location_name).first()
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
    if allow_access("admins") is not None: return allow_access("admins")
    keyword = request.args.get('keyword')
    draft_unis_query = Uni.query.filter_by(is_draft=True).all()
    published_unis_query = Uni.query.filter_by(is_draft=False).all()
    
    if keyword is not None and keyword != '':
        draft_unis_query=sort_by_similarity(draft_unis_query, keyword, 'name')
        published_unis_query=sort_by_similarity(published_unis_query, keyword, 'name')

    courses = []
    locations=[]
    courses_query= Course.query.with_entities(Course.name).all()
    locations_query = Location.query.with_entities(Location.exact_location).all()
    
    for course in courses_query:
        courses.append((course.name, course.name))

    for location in locations_query:
        locations.append((location.exact_location, location.exact_location))

    form = FilterForm(formdata = request.form, courses=courses, locations=locations)

    draft_unis = []
    published_unis = []
    
    for uni in draft_unis_query:
        draft_unis.append(uni)
    for uni in published_unis_query:
        published_unis.append(uni)
    
    for unis in [draft_unis, published_unis]:
        if form.validate_on_submit():
            if form.submit.data:
                for filter in ['ib_cutoff', 'requirements', 'scholarships']:
                    if getattr(form, filter).data!="":
                        unis=sort_by_similarity(unis, getattr(form, filter).data, filter)
                for filter in ['courses', 'location']:
                    if len(getattr(form, filter).data)!=0:
                        for item in getattr(form, filter).data:
                            unis=sort_by_similarity(unis, item, filter)

            if form.submit.data:
                for uni in Uni.query.filter_by(is_draft=False).all():
                    if not uni in unis:
                        unis.append(uni)

    d_unis_len=len(draft_unis_query)
    p_unis_len=len(published_unis_query)
    flash = "University Deleted Successfully!"

    return render_template("manage_unis.html", published_unis = published_unis, form=form, draft_unis=draft_unis, d_unis_len=d_unis_len, p_unis_len=p_unis_len, flash=flash)

@app.route("/manage_courses", methods=['GET', 'POST'])
@login_required
def manage_courses():
    if allow_access("admins") is not None: return allow_access("admins")
    keyword = request.args.get('keyword')
    courses_query= Course.query.with_entities(Course.id, Course.name).all()
    
    if keyword is not None and keyword != '':
        courses_query=sort_by_similarity(courses_query, keyword, 'name')

    courses = []
    
    for course in courses_query:
        courses.append(course)

    courses_len=len(courses)
    flash = "Course Deleted Successfully!"

    return render_template("manage_courses.html", courses = courses, courses_len=courses_len, flash=flash)

@app.route('/delete_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def delete_course(course_id):
    if allow_access("admins") is not None: return allow_access("admins")
    course = Course.query.filter_by(id = course_id).first_or_404()
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('manage_courses'))

@app.route('/edit_course/<int:course_id>/<string:course_name>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id, course_name):
    if allow_access("admins") is not None: return allow_access("admins")
    new_course = Course.query.filter_by(name = course_name).first()
    if new_course:
        if new_course.id != course_id:
            flash("A course with this name already exists.")
            return
    Course.query.filter_by(id = course_id).update(dict(name = course_name))
    db.session.commit()
    return redirect(url_for('manage_courses'))

@app.route("/manage_locations", methods=['GET', 'POST'])
@login_required
def manage_locations():
    if allow_access("admins") is not None: return allow_access("admins")
    keyword = request.args.get('keyword')
    locations_query= Location.query.all()
    
    if keyword is not None and keyword != '':
        locations_query=sort_by_similarity(locations_query, keyword, 'exact_location')

    locations = []
    
    for location in locations_query:
        locations.append(location)

    locations_len=len(locations)
    flash = "Location Deleted Successfully!"

    return render_template("manage_locations.html", locations = locations, locations_len=locations_len, flash=flash)

@app.route('/delete_location/<int:location_id>', methods=['GET', 'POST'])
@login_required
def delete_location(location_id):
    if allow_access("admins") is not None: return allow_access("admins")
    location = Location.query.filter_by(id = location_id).first_or_404()
    db.session.delete(location)
    db.session.commit()
    return redirect(url_for('manage_locations'))

@app.route('/edit_location/<int:location_id>/<string:location_name>', methods=['GET', 'POST'])
@login_required
def edit_location(location_id, location_name):
    if allow_access("admins") is not None: return allow_access("admins")
    if ', ' in location_name:
        split = location_name.split(", ")
        city=split[0]
        country=split[1]
    elif ',' in location_name:
        split = location_name.split(",")
        city=split[0]
        country=split[1]
    else:
        city=location_name
        country="Unknown"

    exact_location = city+", "+country
    new_location = Location.query.filter_by(exact_location = exact_location).first()
    if new_location:
        if new_location.id != location_id:
            flash("A location with this name already exists.")
            return
    Location.query.filter_by(id = location_id).update(dict(city = city, country = country, exact_location = exact_location))
    db.session.commit()
    return redirect(url_for('manage_locations'))

@app.route('/uni/<string:uni_name>', methods=['GET', 'POST'])
def uni(uni_name):
    uni = Uni.query.filter_by(name = uni_name).first_or_404()
    return render_template("uni.html", uni=uni)

@app.route('/delete_uni/<int:uni_id>', methods=['GET', 'POST'])
@login_required
def delete_uni(uni_id):
    if allow_access("admins") is not None: return allow_access("admins")
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
    if allow_access("admins") is not None: return allow_access("admins")
    old_uni = Uni.query.filter_by(name = uni_name).first_or_404()

    courses = []
    locations=[]
    courses_query= Course.query.with_entities(Course.name).all()
    locations_query = Location.query.with_entities(Location.exact_location).all()

    for course in courses_query:
        courses.append((course.name, course.name))

    for location in locations_query:
        locations.append((location.exact_location, location.exact_location))

    form = AddUniversityForm(obj=old_uni, formdata = request.form, courses=courses, locations=locations)

    if form.validate_on_submit():
        new_uni = Uni.query.filter_by(name=form.name.data).first()
        if new_uni:
            if new_uni.id != old_uni.id:
                flash("A university with this name already exists.")
                return render_template("edit_uni.html", form=form, old_uni=old_uni)
        
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
        elif old_uni.logo:
            filename = old_uni.logo
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
            location = Location.query.filter_by(exact_location = location_name).first()
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
    if allow_access("admins") is not None: return allow_access("admins")
    existing = Course.query.filter_by(name = name).first()
    if not existing:
        course = Course(name = name)
        db.session.add(course)
        db.session.commit()
    return redirect(url_for("add_uni"))

@app.route('/add_location/<string:name>')
@login_required
def add_location(name):
    if allow_access("admins") is not None: return allow_access("admins")
    if ', ' in name:
        name = name.split(", ")
        city=name[0]
        country=name[1]
    elif ',' in name:
        name = name.split(",")
        city=name[0]
        country=name[1]
    else:
        city=name
        country="Unknown"
    exact_location = city + ', ' + country
    location=Location(city=city, country=country, exact_location = exact_location)
    existing = Location.query.filter_by(city=city, country=country).first()
    if not existing:
        db.session.add(location)
        db.session.commit()
    return redirect(url_for("add_uni"))

@app.route("/manage_users", methods=["GET", "POST"])
@login_required
def manage_users():
    if allow_access("SUPERUSER") is not None: return allow_access("SUPERUSER")
    keyword = request.args.get('keyword')
    user_query = User.query.all()
    users = []
    for user in user_query:
        if user.username != "SUPERUSER" and user.is_student == False:
            users.append(user)

    if keyword is not None and keyword!='':
        users = sort_by_similarity(users, keyword, column='username')
    
    if len(users) == 0:
        return render_template("manage_users.html", users=users)
    
    del_flash = "User Deleted successfully!"
    return render_template("manage_users.html", del_flash=del_flash, users=users)
    
@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    if allow_access("SUPERUSER") is not None: return allow_access("SUPERUSER")
    user = User.query.filter_by(id = user_id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('manage_users'))

@app.route('/edit_admin/<int:admin_id>', methods=['GET', 'POST'])
@login_required
def edit_admin(admin_id):
    if current_user.is_authenticated:
        if allow_access("SUPERUSER") is not None: return allow_access("SUPERUSER")
    old_admin = User.query.filter_by(id = admin_id).first_or_404()
    form = EditAdminForm(formdata = request.form)

    if form.validate_on_submit():
        new_admin = User.query.filter_by(username = form.username.data).first()
        if new_admin:
            if new_admin.id != admin_id:
                flash("An admin with this name already exists.")
                return render_template('edit_admin.html', form=form, old_admin=old_admin)
        new_admin = User.query.filter_by(email = form.email.data).first()
        if new_admin:
            if new_admin.id != admin_id:
                flash("This email is already registered.")
                return render_template('edit_admin.html', form=form, old_admin=old_admin)
        new_admin = User.query.filter_by(phone_number = form.phone_number.data).first()
        if new_admin:
            if new_admin.id != admin_id:
                flash("This phone number is already registered.")
                return render_template('edit_admin.html', form=form, old_admin=old_admin)
        
        User.query.filter_by(id=old_admin.id).update(dict(email=form.email.data, username=form.username.data))

        if form.password.data !="":
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            User.query.filter_by(id=old_admin.id).update(dict(password=hashed_password))
    
        db.session.commit()

        flash(f'Admin data updated successfully!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('edit_admin.html', form=form, old_admin=old_admin)


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

            if user.is_student:
                return redirect(next_page) if next_page else redirect(url_for('index'))
            elif user.username != "SUPERUSER":
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

@app.route("/admin_register", methods=['GET', 'POST'])
@login_required
def admin_register():
    if allow_access("SUPERUSER") is not None: return allow_access("SUPERUSER")
    form = AdminRegistrationForm(formdata = request.form)

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    fullname=form.fullname.data,
                    email=form.email.data,
                    phone_number = form.phone_number.data,
                    password=hashed_password)

        db.session.add(user)
        db.session.commit()

        flash(f'Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))

    return render_template('admin_register.html', form=form)

@app.route("/student_register", methods=['GET', 'POST'])
def student_register():
    if current_user.is_authenticated:
        if allow_access("admins") is not None: return allow_access("admins")

    form = StudentRegistrationForm(formdata = request.form)

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    fullname=form.fullname.data,
                    email=form.email.data,
                    phone_number = form.phone_number.data,
                    password=hashed_password,
                    is_student=True)
        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(username = form.username.data).with_entities(User.id).first()
        student_details = Student_details(myp_score = form.myp_score.data,
                                          dp_predicted = form.dp_predicted.data, 
                                          dp_score = form.dp_score.data, 
                                          has_diploma = form.has_diploma.data, 
                                          portfolio = form.portfolio.data,
                                          user_id = user.id)
        db.session.add(student_details)
        db.session.commit()

        flash(f'Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))

    return render_template('student_register.html', form=form)

@app.route("/manage_students")
def manage_students():
    if allow_access("admins") is not None: return allow_access("admins")
    students = User.query.filter_by(is_student = True).all()
    student_details = []
    for student in students:
        student_details.append(Student_details.query.filter_by(user_id = student.id).first())
    return render_template('manage_students.html', students = students, student_details = student_details)

@app.route('/delete_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def delete_student(student_id):
    if current_user.id != student_id:
        if allow_access("admins") is not None: return allow_access("admins")

    student = User.query.filter_by(id = student_id).first_or_404()
    db.session.delete(student.student_details)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('manage_students'))

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    if current_user.id != student_id:
        if allow_access("admins") is not None: return allow_access("admins")

    old_student = User.query.filter_by(id = student_id).first_or_404()
    old_student_details = Student_details.query.filter_by(user_id = old_student.id).first_or_404()
    form = EditStudentForm(formdata = request.form)

    if form.validate_on_submit():
        new_student = User.query.filter_by(username = form.username.data).first()
        if new_student:
            if new_student.id != student_id:
                flash("A student with this name already exists.")
                return render_template('edit_student.html', form=form, old_student=old_student)
        new_student = User.query.filter_by(email = form.email.data).first()
        if new_student:
            if new_student.id != student_id:
                flash("This email is already registered.")
                return render_template('edit_student.html', form=form, old_student=old_student)
        new_student = User.query.filter_by(phone_number = form.phone_number.data).first()
        if new_student:
            if new_student.id != student_id:
                flash("This phone number is already registered.")
                return render_template('edit_student.html', form=form, old_student=old_student)
        
        User.query.filter_by(id=old_student.id).update(dict(email=form.email.data, 
                                                            username=form.username.data,
                                                            phone_number=form.phone_number.data,
                                                            fullname = form.fullname.data))
        
        Student_details.query.filter_by(user_id = old_student.id).update(dict(
            myp_score = form.myp_score.data,
            dp_predicted = form.dp_predicted.data,
            dp_score = form.dp_score.data,
            has_diploma = form.has_diploma.data,
            portfolio = form.portfolio.data,
        ))

        if form.password.data !="":
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            User.query.filter_by(id=old_student.id).update(dict(password=hashed_password))
    
        db.session.commit()

        flash(f'Student data updated successfully!', 'success')
        return redirect(url_for('manage_students'))

    return render_template('edit_student.html', form=form, old_student=old_student, old_student_details=old_student_details)


@app.route('/student/<string:student_name>', methods=['GET', 'POST'])
@login_required
def student(student_name):
    if current_user.username != student_name:
        if allow_access("admins") is not None: return allow_access("admins")
    student = User.query.filter_by(username = student_name).first_or_404()
    student_details = Student_details.query.filter_by(user_id = student.id).first_or_404()
    return render_template("student.html", student=student, student_details=student_details)

@app.route('/add_application', methods=['GET', 'POST'])
@login_required
def add_application():
    return

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def access_restricted(e):
    return render_template('403.html'), 403