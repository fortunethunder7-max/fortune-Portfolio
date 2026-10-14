from dotenv import load_dotenv

load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ---------------- Email (Gmail) Configuration ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'fortunethunder7@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')  # Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'fortunethunder7@gmail.com')
app.config['MAIL_RECIPIENT'] = 'fortunethunder7@gmail.com'

mail = Mail(app)
db = SQLAlchemy(app)

# ---------------- Models ----------------
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Contact {self.name}>'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    tech_stack = db.Column(db.String(200))
    link = db.Column(db.String(300))

    def __repr__(self):
        return f'<Project {self.title}>'


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    percentage = db.Column(db.Integer, default=80)
    category = db.Column(db.String(50))

    def __repr__(self):
        return f'<Skill {self.name}>'


# ---------------- Routes ----------------
@app.route('/')
def index():
    skills = Skill.query.all()
    projects = Project.query.limit(3).all()
    return render_template('index.html', skills=skills, projects=projects)


@app.route('/about')
def about():
    skills = Skill.query.all()
    return render_template('about.html', skills=skills)


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/portfolio')
def portfolio():
    category = request.args.get('category', 'all')
    if category == 'all':
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by(category=category).all()
    return render_template('portfolio.html', projects=projects, selected=category)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject') or 'New message from portfolio'
        message = request.form.get('message')

        if not name or not email or not message:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('contact'))

        # 1. Save to database
        new_contact = Contact(name=name, email=email, subject=subject, message=message)
        db.session.add(new_contact)
        db.session.commit()

        # 2. Send email notification to Isaac's Gmail
        try:
            msg = Message(
                subject=f"📩 Portfolio Contact: {subject}",
                recipients=[app.config['MAIL_RECIPIENT']],
                reply_to=email,
                body=(
                    f"New message from your portfolio website:\n\n"
                    f"👤 Name:    {name}\n"
                    f"📧 Email:   {email}\n"
                    f"📝 Subject: {subject}\n"
                    f"🕒 Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"----- Message -----\n{message}\n"
                ),
                html=f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                            background:#0a0e1a;color:#e6edf3;padding:24px;border-radius:12px;">
                    <h2 style="color:#2563eb;margin:0 0 16px 0;">
                        New Portfolio Contact Message
                    </h2>
                    <p style="margin:4px 0;"><strong>👤 Name:</strong> {name}</p>
                    <p style="margin:4px 0;"><strong>📧 Email:</strong>
                        <a href="mailto:{email}" style="color:#f97316;">{email}</a></p>
                    <p style="margin:4px 0;"><strong>📝 Subject:</strong> {subject}</p>
                    <p style="margin:4px 0;"><strong>🕒 Time:</strong>
                        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <hr style="border:none;border-top:1px solid #2a3348;margin:16px 0;">
                    <p style="white-space:pre-wrap;line-height:1.6;">{message}</p>
                    <hr style="border:none;border-top:1px solid #2a3348;margin:16px 0;">
                    <p style="color:#8b96a8;font-size:12px;">
                        Sent from your portfolio website • Isaac
                    </p>
                </div>
                """
            )
            mail.send(msg)
            flash('✅ Message sent successfully! I will get back to you soon.', 'success')
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")
            # Message is still saved in DB — so nothing is lost
            flash('✅ Message received! (Email notification had an issue, but I got your message.)', 'success')

        return redirect(url_for('contact'))

    return render_template('contact.html')
@app.errorhandler(404)
def not_found(e):
    return render_template('base.html', error="404 - Page not found"), 404


# ---------------- Seed Data ----------------
def seed_data():
    if Skill.query.count() == 0:
        skills_data = [
            # Cybersecurity
            ('Penetration Testing', 85, 'cybersecurity'),
            ('Network Security', 80, 'cybersecurity'),
            ('Ethical Hacking', 82, 'cybersecurity'),
            ('Threat Analysis', 78, 'cybersecurity'),
            # Web Design
            ('HTML5 & CSS3', 95, 'webdesign'),
            ('Responsive Design', 92, 'webdesign'),
            ('UI/UX Design', 85, 'webdesign'),
            # Web Development
            ('Python', 92, 'webdev'),
            ('Flask', 90, 'webdev'),
            ('MySQL', 88, 'webdev'),
            ('JavaScript', 82, 'webdev'),
            # Digital Marketing
            ('SEO', 88, 'marketing'),
            ('Social Media Marketing', 85, 'marketing'),
            ('Content Strategy', 87, 'marketing'),
            ('Google Analytics', 83, 'marketing'),
        ]
        for name, pct, cat in skills_data:
            db.session.add(Skill(name=name, percentage=pct, category=cat))

    if Project.query.count() == 0:
        projects_data = [
            ('Security Audit Platform',
             'A comprehensive web platform for performing security audits, vulnerability scanning, and reporting for small businesses.',
             'cybersecurity', 'Python, Flask, MySQL', '#'),
            ('E-Commerce Website',
             'Full-featured e-commerce site with cart, payment integration, and admin dashboard.',
             'webdev', 'Flask, MySQL, HTML/CSS, JavaScript', '#'),
            ('Corporate Business Website',
             'Modern responsive corporate website with blog and CMS features.',
             'webdesign', 'HTML5, CSS3, Flask', '#'),
            ('SEO Marketing Campaign',
             'Digital marketing campaign that increased organic traffic by 250% for a local business.',
             'marketing', 'SEO, Google Analytics, Content Strategy', '#'),
            ('Vulnerability Scanner Tool',
             'Custom Python-based vulnerability scanner for testing web application security.',
             'cybersecurity', 'Python, Nmap, Requests', '#'),
            ('Portfolio CMS',
             'A content management system built with Flask and MySQL for managing portfolio content.',
             'webdev', 'Flask, MySQL, Bootstrap', '#'),
        ]
        for title, desc, cat, tech, link in projects_data:
            db.session.add(Project(title=title, description=desc, category=cat, tech_stack=tech, link=link))

    db.session.commit()


# ---------------- API ----------------
@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email') or not data.get('message'):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    c = Contact(name=data['name'], email=data['email'],
                subject=data.get('subject', ''), message=data['message'])
    db.session.add(c)
    db.session.commit()

    try:
        msg = Message(
            subject=f"📩 Portfolio Contact: {data.get('subject', 'New message')}",
            recipients=[app.config['MAIL_RECIPIENT']],
            reply_to=data['email'],
            body=f"From: {data['name']} <{data['email']}>\n\n{data['message']}"
        )
        mail.send(msg)
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

    return jsonify({'status': 'success', 'message': 'Message received'}), 201
# ---------------- Main ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)