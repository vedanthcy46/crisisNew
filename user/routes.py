import os
from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import Incident, User
from forms import IncidentForm
from utils import allowed_file, save_uploaded_file, user_required
from . import user_bp

@user_bp.route('/dashboard')
@login_required
@user_required
def dashboard():
    # Get user's recent incidents
    recent_incidents = Incident.query.filter_by(reported_by=current_user.id)\
                                   .order_by(Incident.created_at.desc())\
                                   .limit(5).all()
    
    # Get statistics
    total_incidents = Incident.query.filter_by(reported_by=current_user.id).count()
    pending_incidents = Incident.query.filter_by(reported_by=current_user.id, status='pending').count()
    resolved_incidents = Incident.query.filter_by(reported_by=current_user.id, status='resolved').count()
    
    stats = {
        'total': total_incidents,
        'pending': pending_incidents,
        'in_progress': Incident.query.filter_by(reported_by=current_user.id, status='in_progress').count(),
        'resolved': resolved_incidents
    }
    
    return render_template('user/dashboard.html', 
                         recent_incidents=recent_incidents,
                         stats=stats)

@user_bp.route('/report-incident', methods=['GET', 'POST'])
@login_required
@user_required
def report_incident():
    form = IncidentForm()
    
    if form.validate_on_submit():
        try:
            # Handle file upload
            image_path = None
            if form.image.data:
                image_path = save_uploaded_file(form.image.data, 'incidents')
            
            # Create new incident
            incident = Incident(
                title=form.title.data,
                description=form.description.data,
                incident_type=form.incident_type.data,
                priority=form.priority.data,
                address=form.address.data,
                latitude=float(form.latitude.data) if form.latitude.data else None,
                longitude=float(form.longitude.data) if form.longitude.data else None,
                image_path=image_path,
                reported_by=current_user.id
            )
            
            db.session.add(incident)
            db.session.commit()
            
            flash('Incident reported successfully! Our team will respond shortly.', 'success')
            current_app.logger.info(f'New incident reported by {current_user.username}: {incident.title}')
            return redirect(url_for('user.my_incidents'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while reporting the incident. Please try again.', 'error')
            current_app.logger.error(f'Error reporting incident: {str(e)}')
    
    return render_template('user/report_incident.html', form=form)

@user_bp.route('/my-incidents')
@login_required
@user_required
def my_incidents():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    incidents = Incident.query.filter_by(reported_by=current_user.id)\
                             .order_by(Incident.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('user/my_incidents.html', incidents=incidents)

@user_bp.route('/incident/<int:incident_id>')
@login_required
@user_required
def view_incident(incident_id):
    incident = Incident.query.filter_by(id=incident_id, reported_by=current_user.id).first_or_404()
    
    # Get status updates for this incident
    status_updates = incident.status_updates.order_by(db.desc('created_at')).all()
    
    return render_template('user/incident_details.html', 
                         incident=incident,
                         status_updates=status_updates)

@user_bp.route('/profile')
@login_required
@user_required
def profile():
    return render_template('user/profile.html')
