from main.forms import LoginForm, AdminRegistrationForm, EditAdminForm, AddUniversityForm, StudentRegistrationForm, EditStudentForm, ApplicationForm, FilterForm, FilterStudentsForm
from main.setup import app, db
from main.models import User, Uni, Location, Course, Student_details, Application
from main.helper import sort_by_similarity, allow_access, GetAppAndAddNo
from main import bcrypt

from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from dotenv import load_dotenv
import os

load_dotenv()

HASHED_SUPER_USER_KEY = os.getenv('HASHED_SUPER_USER_KEY')

@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/unis", methods=["GET", "POST"])
@login_required
def unis():
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

    form = FilterForm(formdata = request.form, courses=courses, locations = locations)

    if form.validate_on_submit():
        unis= Uni.query.filter_by(is_draft=False)
        if form.submit.data:
            for filter in ['acceptance_rate', 'gpa','ib_cutoff', 'avg_cost']:
                if getattr(form, 'min_'+filter).data!="":
                    unis=unis.filter(getattr(Uni, filter)>=getattr(form, 'min_'+filter).data)
                if getattr(form, 'max_'+filter).data!="":
                    unis=unis.filter(getattr(Uni, filter)<=getattr(form, 'max_'+filter).data)
            unis=unis.all()

            for filter in ['requirements', 'scholarships']:
                if getattr(form, filter).data!="":
                    unis=sort_by_similarity(unis, getattr(form, filter).data, filter)
            for filter in ['courses', 'locations']:
                if len(getattr(form, filter).data)!=0:
                    for item in getattr(form, filter).data:
                        unis=sort_by_similarity(unis, item, filter)
            
            if form.coisstudents.data:
                no_add, no_app = GetAppAndAddNo(unis)
                temp = unis
                unis = []
                for i in range(len(temp)):
                    if no_add[i] + no_app[i] != 0:
                        unis.append(temp[i])
                
            for uni in Uni.query.filter_by(is_draft=False).all():
                if uni not in unis:
                    unis.append(uni)

            no_add, no_app = GetAppAndAddNo(unis)
            return render_template("unis.html", unis=unis, form=form, courses=courses, locations=locations, no_add = no_add, no_app = no_app, len = len, zip = zip)
    
    no_add, no_app = GetAppAndAddNo(unis)
    return render_template("unis.html", unis=unis, form=form, courses=courses, locations=locations, no_add = no_add, no_app = no_app, len = len, zip = zip)

@app.route("/add_uni", methods=['GET', 'POST'])
@login_required
def add_uni():
    if allow_access("admins") is not None: return allow_access("admins")
    courses=[]
    locations=[]
    courses_query= Course.query.with_entities(Course.name).all()
    locations_query = Location.query.all()

    for course in courses_query:
        courses.append((course.name, course.name))

    for location in locations_query:
        locations.append((location.id, location.exact_location))

    form = AddUniversityForm(formdata = request.form, courses=courses, locations=locations)

    if form.validate_on_submit():
        if Uni.query.filter_by(name = form.name.data).first():
            flash('A university with this name has been added eariler.')
            return render_template("add_uni.html", form=form)
        
        if not form.website.data or not form.ib_cutoff.data or len(form.courses.data) == 0:
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

        logo = request.files['logo']
        banner = request.files['banner']
        if logo:
            logo_filename = form.name.data + '.' + logo.filename.rsplit('.', 1)[1].lower()
            logo.save(os.path.join(app.root_path, 'static', 'university_logos', logo_filename))
        else:
            logo_filename = None
            is_draft = True
        if banner:
            banner_filename = form.name.data + '.' + banner.filename.rsplit('.', 1)[1].lower()
            banner.save(os.path.join(app.root_path, 'static', 'university_banners', banner_filename))
        else:
            banner_filename = None
            is_draft = True
            
        uni = Uni(name = form.name.data, location = Location.query.filter_by(exact_location = form.location.data).first(), logo = logo_filename, banner=banner_filename, website= form.website.data, ib_cutoff=form.ib_cutoff.data, scholarships=form.scholarships.data, requirements=form.requirements.data, email=form.email.data, min_gpa = form.min_gpa.data, avg_cost=form.avg_cost.data, acceptance_rate=form.acceptance_rate.data, is_draft=is_draft)
        
        for course_name in form.courses.data:
            course = Course.query.filter_by(name=course_name).first()
            uni.courses.append(course)
            course.unis.append(uni)

        db.session.add(uni)
        db.session.commit()

        if is_draft:
            flash("University saved as draft!", 'success')
        else:
            flash("University added successfully!", 'success')

        return redirect(url_for('manage_unis'))

    return render_template("add_uni.html", form=form, locations=locations)


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
        
    d_unis_len=len(draft_unis_query)
    p_unis_len=len(published_unis_query)
    flash = "University Deleted Successfully!"
    
    if form.validate_on_submit():
        if form.submit.data:
            draft_unis = Uni.query.filter_by(is_draft=True)
            published_unis = Uni.query.filter_by(is_draft=False)
            
            for filter in ['acceptance_rate', 'gpa','ib_cutoff', 'avg_cost']:
                if getattr(form, 'min_'+filter).data!="":
                    published_unis=published_unis.filter(getattr(Uni, filter)>=getattr(form, 'min_'+filter).data)
                if getattr(form, 'max_'+filter).data!="":
                    published_unis=published_unis.filter(getattr(Uni, filter)<=getattr(form, 'max_'+filter).data)
            published_unis=published_unis.all()

            for filter in ['requirements', 'scholarships', 'location']:
                if getattr(form, filter).data!="":
                    published_unis=sort_by_similarity(published_unis, getattr(form, filter).data, filter)
            for filter in ['courses']:
                if len(getattr(form, filter).data)!=0:
                    for item in getattr(form, filter).data:
                        published_unis=sort_by_similarity(published_unis, item, filter)


            for filter in ['acceptance_rate', 'gpa','ib_cutoff', 'avg_cost']:
                if getattr(form, 'min_'+filter).data!="":
                    draft_unis=draft_unis.filter(getattr(Uni, filter)>=getattr(form, 'min_'+filter).data)
                if getattr(form, 'max_'+filter).data!="":
                    draft_unis=draft_unis.filter(getattr(Uni, filter)<=getattr(form, 'max_'+filter).data)
            draft_unis=draft_unis.all()

            for filter in ['requirements', 'scholarships', 'location']:
                if getattr(form, filter).data!="":
                    draft_unis=sort_by_similarity(draft_unis, getattr(form, filter).data, filter)
            for filter in ['courses']:
                if len(getattr(form, filter).data)!=0:
                    for item in getattr(form, filter).data:
                        draft_unis=sort_by_similarity(draft_unis, item, filter)
            
            
            if form.coisstudents.data:
                no_add, no_app = GetAppAndAddNo(published_unis)
                temp = published_unis
                published_unis = []
                for i in range(len(temp)):
                    if no_add[i] + no_app[i] != 0:
                        published_unis.append(temp[i])
                
            for uni in Uni.query.filter_by(is_draft=False).all():
                if uni not in published_unis:
                    published_unis.append(uni)

            for uni in Uni.query.filter_by(is_draft=True).all():
                if uni not in draft_unis:
                    draft_unis.append(uni)

            no_add, no_app = GetAppAndAddNo(published_unis)
            return render_template("manage_unis.html", published_unis = published_unis, form=form, draft_unis=draft_unis, d_unis_len=d_unis_len, p_unis_len=p_unis_len, zip=zip, no_add = no_add, no_app = no_app, flash=flash)
    
    no_add, no_app = GetAppAndAddNo(published_unis)
    return render_template("manage_unis.html", published_unis = published_unis, form=form, draft_unis=draft_unis, d_unis_len=d_unis_len, p_unis_len=p_unis_len, zip=zip, no_add = no_add, no_app = no_app, flash=flash)

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
@login_required
def uni(uni_name):
    uni = Uni.query.filter_by(name = uni_name).first_or_404()
    admission_students = Student_details.query.filter_by(selected_uni_id = uni.id).all()
    admissions = []
    admission_ids = []
    for student in admission_students:
        admissions.append({
            'details': student, 
            'application': Application.query.filter_by(id = student.selected_app_id).first(),
            'user': User.query.filter_by(id = student.user_id).first()
        })
        admission_ids.append(student.id)

    others=[]
    for application in Application.query.filter_by(uni_id = uni.id).all():
        if application.student_id not in admission_ids:
            student = Student_details.query.filter_by(id = application.student_id).first()
            others.append({
                'details': student,
                'application': application,
                'user': User.query.filter_by(id = student.user_id).first()
            })

    return render_template("uni.html", uni=uni, admissions=admissions, others=others, len=len, zip=zip, range=range)

@app.route('/delete_uni/<int:uni_id>', methods=['GET', 'POST'])
@login_required
def delete_uni(uni_id):
    if allow_access("admins") is not None: return allow_access("admins")
    uni = Uni.query.filter_by(id = uni_id).first_or_404()

    courses = uni.courses
    for course in courses:
        course.unis.remove(uni)

    if uni.logo:
        os.remove(os.path.join(app.root_path, 'static', 'university_logos', uni.logo))
    if uni.banner:
        os.remove(os.path.join(app.root_path, 'static', 'university_banners', uni.banner))
    
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
    locations_query = Location.query.all()

    for course in courses_query:
        courses.append((course.name, course.name))

    for location in locations_query:
        locations.append((location.id, location.exact_location))

    form = AddUniversityForm(obj=old_uni, formdata = request.form, courses=courses, locations=locations)

    if form.validate_on_submit():
        new_uni = Uni.query.filter_by(name=form.name.data).first()
        if new_uni:
            if new_uni.id != old_uni.id:
                flash("A university with this name already exists.")
                return render_template("edit_uni.html", form=form, old_uni=old_uni)
        
        if not form.website.data or not form.ib_cutoff.data or len(form.courses.data) == 0:
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
        
        logo = request.files['logo']
        banner = request.files['banner']
        if logo:
            logo_filename = form.name.data + '.' + logo.filename.rsplit('.', 1)[1].lower()
            logo.save(os.path.join(app.root_path, 'static', 'university_logos', logo_filename))
        elif old_uni.logo:
            logo_filename = old_uni.logo
        else:
            logo_filename = None
            is_draft = True
        if banner:
            banner_filename = form.name.data + '.' + banner.filename.rsplit('.', 1)[1].lower()
            banner.save(os.path.join(app.root_path, 'static', 'university_banners', banner_filename))
        elif old_uni.banner:
            banner_filename = old_uni.banner
        else:
            banner_filename = None
            is_draft = True

        new_uni = Uni(id=old_uni.id, name = form.name.data, location = Location.query.filter_by(exact_location = form.location.data).first(), logo = logo_filename, banner=banner_filename, website= form.website.data, ib_cutoff=form.ib_cutoff.data, scholarships=form.scholarships.data, requirements=form.requirements.data, email=form.email.data, min_gpa = form.min_gpa.data, avg_cost=form.avg_cost.data, acceptance_rate=form.acceptance_rate.data, is_draft=is_draft)
        db.session.delete(old_uni)
        db.session.add(new_uni)
        
        for course_name in form.courses.data:
            course = Course.query.filter_by(name=course_name).first()
            new_uni.courses.append(course)
            course.unis.append(new_uni)

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

@app.route("/manage_admins", methods=["GET", "POST"])
@login_required
def manage_admins():
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
        return render_template("manage_admins.html", users=users)
    
    del_flash = "User Deleted successfully!"
    return render_template("manage_admins.html", del_flash=del_flash, users=users)
    
@app.route('/delete_admin/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_admin(user_id):
    if current_user.id != user_id:
        if allow_access("SUPERUSER") is not None: return allow_access("SUPERUSER")
    user = User.query.filter_by(id = user_id).first_or_404()

    if user.pfp != "default.png":
        os.remove(os.path.join(app.root_path, 'profile_pics', user.pfp))

    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('manage_admins'))

@app.route('/edit_admin/<int:admin_id>', methods=['GET', 'POST'])
@login_required
def edit_admin(admin_id):
    if current_user.id != admin_id:
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
        
        f = request.files['pfp']
        if f:
            filename = form.username.data + '.' + f.filename.rsplit('.', 1)[1].lower()
            f.save(os.path.join(app.root_path, 'static', 'profile_pics', filename))
        else:
            filename=old_admin.pfp
        
        User.query.filter_by(id=old_admin.id).update(dict(email=form.email.data, username=form.username.data, fullname=form.fullname.data.title(), pfp=filename))

        if form.password.data !="":
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            User.query.filter_by(id=old_admin.id).update(dict(password=hashed_password))
    
        db.session.commit()

        flash(f'Admin data updated successfully!', 'success')
        if current_user.id ==old_admin.id:
            return redirect(url_for('profile', username = current_user.username))
        else:
            return redirect(url_for('manage_admins'))

    return render_template('edit_admin.html', form=form, old_admin=old_admin)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and current_user.is_student:
        return redirect(url_for('unis'))
    elif current_user.is_authenticated and not current_user.is_student:
        return redirect(url_for('manage_unis'))
    form = LoginForm(formdata = request.form)

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')

            if user.is_student:
                return redirect(next_page) if next_page else redirect(url_for('unis'))
            elif user.username != "SUPERUSER":
                return redirect(next_page) if next_page else redirect(url_for('manage_unis'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('manage_admins'))
        else:
            flash('Login Unsuccessful, Please Check Your Username And Password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged Out Successfully!")
    return redirect(url_for('unis'))

@app.route("/admin_register", methods=['GET', 'POST'])
@login_required
def admin_register():
    if allow_access("SUPERUSER") is not None: return allow_access("SUPERUSER")
    form = AdminRegistrationForm(formdata = request.form)

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        f = request.files['pfp']
        if f:
            filename = form.username.data + '.' + f.filename.rsplit('.', 1)[1].lower()
            f.save(os.path.join(app.root_path, 'static', 'profile_pics', filename))
        else:
            filename="default.png"

        user = User(username=form.username.data,
                    fullname=form.fullname.data.title(),
                    email=form.email.data,
                    phone_number = form.phone_number.data,
                    password=hashed_password,
                    pfp = filename)

        db.session.add(user)
        db.session.commit()

        flash(f'Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))

    return render_template('admin_register.html', form=form)

@app.route("/student_register", methods=['GET', 'POST'])
def student_register():
    if current_user.is_authenticated:
        if allow_access("admins") is not None: return allow_access("admins")
        logout_user()

    form = StudentRegistrationForm(formdata = request.form)

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        f = request.files['pfp']
        if f:
            filename = form.username.data + '.' + f.filename.rsplit('.', 1)[1].lower()
            f.save(os.path.join(app.root_path, 'static', 'profile_pics', filename))
        else:
            filename="default.png"

        user = User(username=form.username.data,
                    fullname=form.fullname.data.title(),
                    email=form.email.data,
                    phone_number = form.phone_number.data,
                    password=hashed_password,
                    is_student=True,
                    pfp=filename)
        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(username = form.username.data).with_entities(User.id).first()
        student_details = Student_details(myp_score = form.myp_score.data,
                                          dp_predicted = form.dp_predicted.data, 
                                          dp_score = form.dp_score.data, 
                                          has_diploma = form.has_diploma.data, 
                                          portfolio = form.portfolio.data,
                                          graduation_year = form.graduation_year.data,
                                          user_id = user.id)
        db.session.add(student_details)
        db.session.commit()

        flash(f'Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))

    return render_template('student_register.html', form=form)

@app.route("/manage_students")
@login_required
def manage_students():
    if allow_access("admins") is not None: return allow_access("admins")
    students = User.query.filter_by(is_student = True).all()
    student_details = []
    for student in students:
        student_details.append(Student_details.query.filter_by(user_id = student.id).first())
    
    del_flash = "Student Deleted successfully!"

    return render_template('manage_students.html', students = students, student_details = student_details, zip=zip, del_flash=del_flash)

@app.route('/delete_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def delete_student(student_id):
    if current_user.id != student_id:
        if allow_access("admins") is not None: return allow_access("admins")

    student = User.query.get_or_404(student_id)
    
    if student.pfp != "default.png" and student.pfp is not None:
        os.remove(os.path.join(app.root_path, 'static', 'profile_pics', student.pfp))
    
    student_detail = Student_details.query.filter_by(user_id=student_id).first()
    db.session.delete(student_detail)

    applications = Application.query.filter_by(user_id=student_detail.id).all()
    for application in applications:
        db.session.delete(application)

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
        
        f = request.files['pfp']
        if f:
            filename = form.username.data + '.' + f.filename.rsplit('.', 1)[1].lower()
            f.save(os.path.join(app.root_path, 'static', 'profile_pics', filename))
        else:
            filename=old_student.pfp
        
        User.query.filter_by(id=old_student.id).update(dict(email=form.email.data, 
                                                            username=form.username.data,
                                                            phone_number=form.phone_number.data,
                                                            fullname = form.fullname.data.title(),
                                                            pfp=filename))
        
        Student_details.query.filter_by(user_id = old_student.id).update(dict(
            myp_score = form.myp_score.data,
            dp_predicted = form.dp_predicted.data,
            dp_score = form.dp_score.data,
            has_diploma = form.has_diploma.data,
            portfolio = form.portfolio.data,
            graduation_year = form.graduation_year.data,
        ))

        if form.password.data !="":
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            User.query.filter_by(id=old_student.id).update(dict(password=hashed_password))
    
        db.session.commit()

        if current_user.id ==old_student.id:
            flash(f'Profile updated successfully!', 'success')
            return redirect(url_for('profile', username = current_user.username))
        else:
            flash(f'Student data updated successfully!', 'success')
            return redirect(url_for('manage_admins'))

    return render_template('edit_student.html', form=form, old_student=old_student, old_student_details=old_student_details)

@app.route('/add_application', methods=['GET', 'POST'])
@login_required
def add_application():
    if allow_access("only_students") is not None: return allow_access("only_students")
    student_details = Student_details.query.filter_by(user_id=current_user.id).with_entities(Student_details.id).first_or_404()    
    courses=[]
    minors=[]
    unis=[]
    locations=[]
    courses_query= Course.query.with_entities(Course.id, Course.name).all()
    unis_query = Uni.query.with_entities(Uni.id, Uni.name).all()

    for course in courses_query:
        courses.append((course.id, course.name))
    for course in courses_query:
        minors.append((course.name, course.name))
    for uni in unis_query:
        unis.append((uni.id, uni.name))

    form = ApplicationForm(formdata = request.form, courses=courses, minors=minors, unis=unis, locations=locations)
    if form.validate_on_submit():
        application=Application(uni_id = int(form.uni.data),
            student_id = int(student_details.id),
            course_id = int(form.course.data),
            location_id = Uni.query.filter_by(id = form.uni.data).first().location_id,
            status = form.status.data,
            scholarship = form.scholarship.data,
            other_details = form.other_details.data,
            is_early = form.is_early.data)

        for minor in form.minors.data:
            course = Course.query.filter_by(name = minor).first()
            application.minors.append(course)
        
        db.session.add(application)
        db.session.commit()
        
        if form.selected_uni.data:
            application = Application.query.filter_by(uni_id = int(form.uni.data),
            student_id = int(student_details.id),
            course_id = int(form.course.data),
            status = form.status.data,
            scholarship = form.scholarship.data,
            other_details = form.other_details.data,
            is_early = form.is_early.data).first()

            Student_details.query.filter_by(user_id = current_user.id).update(dict(selected_app_id=application.id, selected_uni_id=form.uni.data))
            db.session.commit()
            
        return redirect(url_for('profile', username=current_user.username))
            
    return render_template('add_application.html', form=form)


@app.route('/edit_application/<int:application_id>', methods=['GET', 'POST'])
@login_required
def edit_application(application_id):
    old_app = Application.query.filter_by(id = application_id).first_or_404()

    if allow_access("only_students") is not None: return allow_access("only_students")
    
    application = Application.query.get_or_404(application_id)
    student_details = Student_details.query.filter_by(user_id=current_user.id).with_entities(Student_details.id, Student_details.selected_app_id).first_or_404()

    selected_app = student_details.selected_app_id == old_app.id
    
    # Ensure the application belongs to the current user
    if application.student_id != student_details.id:
        abort(403)

    courses = [(course.id, course.name) for course in Course.query.with_entities(Course.id, Course.name).all()]
    minors = [(course.name, course.name) for course in Course.query.with_entities(Course.id, Course.name).all()]
    unis = [(uni.id, uni.name) for uni in Uni.query.with_entities(Uni.id, Uni.name).all()]

    form = ApplicationForm(obj=application, formdata=request.form, courses=courses, minors=minors, unis=unis)
    
    if form.validate_on_submit():
        application.uni_id = int(form.uni.data)
        application.course_id = int(form.course.data)
        application.location_id = Uni.query.filter_by(id = form.uni.data).first().location_id
        application.status = form.status.data
        application.scholarship = form.scholarship.data
        application.other_details = form.other_details.data
        application.is_early = form.is_early.data

        application.minors = []
        for minor in form.minors.data:
            print(type(minor))
            course = Course.query.filter_by(name=minor).first()
            if course:
                application.minors.append(course)

        if form.selected_uni.data:
            Student_details.query.filter_by(user_id=current_user.id).update(dict(selected_app_id=application.id, selected_uni_id=form.uni.data))
        
        if (Student_details.query.filter_by(user_id=current_user.id).first().selected_app_id == old_app.id ) and (not form.selected_uni.data):
            Student_details.query.filter_by(user_id=current_user.id).update(dict(selected_app_id=None, selected_uni_id=None))
        
        db.session.commit()
            
        return redirect(url_for('profile', username=current_user.username))

    return render_template('edit_application.html', form=form, old_app=old_app, application=application, selected_app = selected_app)

@app.route('/delete_application/<int:application_id>', methods=['GET', 'POST'])
@login_required
def delete_application(application_id):
    app = Application.query.filter_by(id = application_id).first_or_404()

    if allow_access("only_students") is not None: return allow_access("only_students")
    
    application = Application.query.get_or_404(application_id)
    student_details = Student_details.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Ensure the application belongs to the current user
    if application.student_id != student_details.id:
        abort(403)
    
    if student_details.selected_app_id == app.id :
        Student_details.query.filter_by(user_id=current_user.id).update(dict(selected_app_id=None, selected_uni_id=None))

    db.session.delete(app)
    db.session.commit()

    return redirect(url_for('profile', username=current_user.username))


@app.route('/profile/<string:username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    if username is None:
        return abort(404)
    
    user = User.query.filter_by(username=username).first_or_404()
    if not user.is_student:
        if username != current_user.username:
            if allow_access("SUPERUSER") is not None: return allow_access("SUPERUSER")
        return render_template("admin_profile.html", user=user)
    else:
        student_details = Student_details.query.filter_by(user_id=user.id).first_or_404()
        applications = Application.query.filter_by(student_id=student_details.id).all()
        return render_template("student_profile.html", student=user, student_details = student_details, applications=applications, len=len)


@app.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    courses=[('None', 'None')]
    minors=[('None', 'None')]
    unis=[('None', 'None')]
    locations=[('None', 'None')]
    courses_query= Course.query.with_entities(Course.id, Course.name).all()
    unis_query = Uni.query.with_entities(Uni.id, Uni.name).all()
    locations_query = Location.query.with_entities(Location.id, Location.exact_location).all()

    for course in courses_query:
        courses.append((course.id, course.name))
    for course in courses_query:
        minors.append((course.name, course.name))
    for uni in unis_query:
        unis.append((uni.id, uni.name))
    for location in locations_query:
        locations.append((location.id, location.exact_location))

    form = FilterStudentsForm(formdata = request.form, courses=courses, minors=minors, unis=unis, locations=locations)
    students = User.query.filter_by(is_student=True).all()
    student_details=[]
    applications=[]
    for student in students:
        details = Student_details.query.filter_by(user_id=student.id).first_or_404()
        student_details.append(details)
        applications.append(Application.query.filter_by(student_id=details.id).all())

    keyword = request.args.get('keyword')
    if keyword is not None and keyword != '':
        students=sort_by_similarity(students, keyword, column='fullname')

    if form.validate_on_submit():
        if form.clear.data:
            return redirect(url_for("students"))
        
        
        app_query = Application.query
        if form.uni.data and form.uni.data != 'None':app_query=app_query.filter_by(uni_id = form.uni.data)
        if form.location.data and form.location.data != 'None':app_query=app_query.filter_by(location_id = form.location.data)
        if form.course.data and form.course.data != 'None':app_query=app_query.filter_by(course_id = form.course.data)
        if form.status.data and form.status.data != 'none':app_query=app_query.filter_by(status = form.status.data)
        if form.is_early.data:app_query=app_query.filter_by(is_early = form.is_early.data)
        if form.selected_uni.data:
            app_query = app_query.filter(Application.id == Student_details.query.filter_by(id = Application.student_id).first().selected_app_id)
        app_query = app_query.with_entities(Application.student_id).all()

        if len(Application.query.all()) != len(app_query):
            ids= [ id[0] for id in app_query ]
            query = Student_details.query.filter(Student_details.id.in_(ids))
        else:
            query = Student_details.query
        
        if form.has_diploma.data: query = query.filter_by(has_diploma = form.has_diploma.data)
        if form.graduation_year.data: query = query.filter_by(graduation_year = form.graduation_year.data)
        if form.myp_score_min.data: query = query.filter(Student_details.myp_score>=form.myp_score_min.data)
        if form.myp_score_max.data: query = query.filter(Student_details.myp_score<=form.myp_score_max.data)
        if form.dp_predicted_min.data: query = query.filter(Student_details.dp_predicted>=form.dp_predicted_min.data)
        if form.dp_predicted_max.data: query = query.filter(Student_details.dp_predicted<=form.dp_predicted_max.data)
        if form.dp_score_min.data: query = query.filter(Student_details.dp_score>=form.dp_score_min.data)
        if form.dp_score_max.data: query = query.filter(Student_details.dp_score<=form.dp_score_max.data)

        student_details=query.all()
        students=[]
        applications=[]
        for details in student_details:
            user = User.query.filter_by(id=details.user_id).first_or_404()
            students.append(user)
            applications.append(Application.query.filter_by(student_id=details.id).all())
        return render_template("students.html", form=form, students=students, student_details=student_details, applications=applications, zip=zip)
    else:
        if form.clear.data:
            return redirect(url_for("students"))    
    
    return render_template("students.html", form=form, students=students, student_details=student_details, applications=applications, zip=zip)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def access_restricted(e):
    return render_template('403.html'), 403