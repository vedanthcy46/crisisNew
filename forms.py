from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, BooleanField, HiddenField, MultipleFileField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class ProfileForm(FlaskForm):
    username = StringField('Username', render_kw={'readonly': True})
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])

class IncidentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    incident_type = SelectField('Incident Type', choices=[
        ('fire', 'Fire'),
        ('medical', 'Medical Emergency'),
        ('accident', 'Accident'),
        ('natural_disaster', 'Natural Disaster'),
        ('crime', 'Crime'),
        ('utility', 'Utility Failure'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    latitude = StringField('Latitude', validators=[Optional()])
    longitude = StringField('Longitude', validators=[Optional()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])

class UserManagementForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    role = SelectField('Role', choices=[
        ('user', 'Regular User'),
        ('rescue_team', 'Rescue Team'),
        ('admin', 'Administrator')
    ], validators=[DataRequired()])
    password = PasswordField('Password (leave blank to keep unchanged)', validators=[Optional(), Length(min=6)])
    
    # Remove the confirm_password field as it's not in the template

class ResourceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    resource_type = SelectField('Type', choices=[
        ('vehicle', 'Vehicle'),
        ('equipment', 'Equipment'),
        ('personnel', 'Personnel'),
        ('medical', 'Medical Supply'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    availability_status = SelectField('Availability Status', choices=[
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('unavailable', 'Unavailable')
    ], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])

class AssignTeamForm(FlaskForm):
    team_id = SelectField('Rescue Team', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])

class AssignResourceForm(FlaskForm):
    resource_ids = SelectField('Resources', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])

class AdminStatusUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('rejected', 'Rejected')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])

class RescueStatusUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    image = FileField('Rescue Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])

class StatusUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])