from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, PasswordField, HiddenField, FloatField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    password2 = PasswordField('Confirm Password', 
                             validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class IncidentForm(FlaskForm):
    title = StringField('Incident Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=1000)])
    incident_type = SelectField('Incident Type', 
                               choices=[
                                   ('fire', 'Fire'),
                                   ('medical', 'Medical Emergency'),
                                   ('accident', 'Traffic Accident'),
                                   ('natural_disaster', 'Natural Disaster'),
                                   ('crime', 'Crime/Security'),
                                   ('utility', 'Utility Emergency'),
                                   ('other', 'Other')
                               ],
                               validators=[DataRequired()])
    priority = SelectField('Priority Level',
                          choices=[
                              ('low', 'Low'),
                              ('medium', 'Medium'),
                              ('high', 'High'),
                              ('critical', 'Critical')
                          ],
                          validators=[DataRequired()],
                          default='medium')
    address = TextAreaField('Address/Location', validators=[DataRequired(), Length(min=5, max=500)])
    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    image = FileField('Upload Image (Optional)', 
                     validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])

class StatusUpdateForm(FlaskForm):
    status = SelectField('Status',
                        choices=[
                            ('pending', 'Pending'),
                            ('in_progress', 'In Progress'),
                            ('resolved', 'Resolved'),
                            ('closed', 'Closed')
                        ],
                        validators=[DataRequired()])
    notes = TextAreaField('Update Notes', validators=[Optional(), Length(max=500)])

class UserManagementForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    role = SelectField('Role',
                      choices=[
                          ('user', 'User'),
                          ('rescue_team', 'Rescue Team'),
                          ('admin', 'Administrator')
                      ],
                      validators=[DataRequired()])
    password = PasswordField('Password (leave blank to keep current)', validators=[Optional(), Length(min=6, max=128)])

class ResourceForm(FlaskForm):
    name = StringField('Resource Name', validators=[DataRequired(), Length(min=2, max=100)])
    resource_type = SelectField('Resource Type',
                               choices=[
                                   ('vehicle', 'Vehicle'),
                                   ('equipment', 'Equipment'),
                                   ('personnel', 'Personnel')
                               ],
                               validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    availability_status = SelectField('Availability Status',
                                     choices=[
                                         ('available', 'Available'),
                                         ('in_use', 'In Use'),
                                         ('maintenance', 'Under Maintenance')
                                     ],
                                     validators=[DataRequired()],
                                     default='available')
    location = StringField('Location', validators=[Optional(), Length(max=200)])

class AssignResourceForm(FlaskForm):
    resource_ids = SelectMultipleField('Resources', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Assignment Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Assign Resources')

class AssignTeamForm(FlaskForm):
    team_id = SelectField('Rescue Team', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Assignment Notes', validators=[Optional(), Length(max=500)])

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6, max=128)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        Optional(), 
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Update Profile')
