from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import event

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # user, rescue_team, admin
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reported_incidents = db.relationship('Incident', foreign_keys='Incident.reported_by', backref='reporter', lazy='dynamic')
    assigned_incidents = db.relationship('Incident', foreign_keys='Incident.assigned_team_id', backref='assigned_team', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_rescue_team(self):
        return self.role == 'rescue_team'
    
    def is_user(self):
        return self.role == 'user'

class Incident(db.Model):
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)  # fire, medical, accident, natural_disaster, etc.
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, in_progress, resolved, closed
    
    # Location information
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.Text)
    
    # File upload - MongoDB image ID
    image_id = db.Column(db.String(24))
    rescue_image_id = db.Column(db.String(24))  # Image uploaded by rescue team
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Foreign keys
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_team_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    resources = db.relationship('IncidentResource', backref='incident', lazy='dynamic', cascade='all, delete-orphan')
    status_updates = db.relationship('StatusUpdate', backref='incident', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Incident {self.title}>'
    
    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'in_progress': 'info',
            'resolved': 'success',
            'closed': 'secondary'
        }
        return colors.get(self.status, 'secondary')
    
    def get_priority_color(self):
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark'
        }
        return colors.get(self.priority, 'secondary')

class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # vehicle, equipment, personnel
    description = db.Column(db.Text)
    availability_status = db.Column(db.String(20), nullable=False, default='available')  # available, in_use, maintenance
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident_assignments = db.relationship('IncidentResource', backref='resource', lazy='dynamic')
    
    def __repr__(self):
        return f'<Resource {self.name}>'
    
    def get_status_color(self):
        colors = {
            'available': 'success',
            'in_use': 'warning',
            'maintenance': 'danger'
        }
        return colors.get(self.availability_status, 'secondary')

class IncidentResource(db.Model):
    __tablename__ = 'incident_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<IncidentResource {self.incident_id}-{self.resource_id}>'

class StatusUpdate(db.Model):
    __tablename__ = 'status_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    updater = db.relationship('User', foreign_keys=[updated_by])
    
    def __repr__(self):
        return f'<StatusUpdate {self.incident_id}: {self.old_status} -> {self.new_status}>'

# Event listeners to update incident resolved_at timestamp
@event.listens_for(Incident.status, 'set')
def incident_status_changed(target, value, oldvalue, initiator):
    if value == 'resolved' and oldvalue != 'resolved':
        target.resolved_at = datetime.utcnow()
    elif value != 'resolved' and oldvalue == 'resolved':
        target.resolved_at = None