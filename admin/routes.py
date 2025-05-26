import os
from flask import render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import func, extract
from app import db
from models import User, Incident, Resource, IncidentResource, StatusUpdate
from forms import UserManagementForm, ResourceForm, AssignResourceForm, AssignTeamForm, StatusUpdateForm
from utils import admin_required
from . import admin_bp

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get overall statistics
    total_users = User.query.filter_by(role='user').count()
    total_rescue_teams = User.query.filter_by(role='rescue_team').count()
    total_incidents = Incident.query.count()
    total_resources = Resource.query.count()
    
    # Get recent incidents
    recent_incidents = Incident.query.order_by(Incident.created_at.desc()).limit(5).all()
    
    # Get incidents by status
    incident_stats = {
        'pending': Incident.query.filter_by(status='pending').count(),
        'in_progress': Incident.query.filter_by(status='in_progress').count(),
        'resolved': Incident.query.filter_by(status='resolved').count(),
        'closed': Incident.query.filter_by(status='closed').count()
    }
    
    # Get high priority incidents
    high_priority_incidents = Incident.query.filter(
        Incident.priority.in_(['high', 'critical']),
        Incident.status.in_(['pending', 'in_progress'])
    ).count()
    
    stats = {
        'total_users': total_users,
        'total_rescue_teams': total_rescue_teams,
        'total_incidents': total_incidents,
        'total_resources': total_resources,
        'high_priority_incidents': high_priority_incidents,
        'incident_stats': incident_stats
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_incidents=recent_incidents)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.order_by(User.created_at.desc())\
                     .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = UserManagementForm()
    
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data,
                phone=form.phone.data,
                address=form.address.data,
                role=form.role.data,
                password_hash=generate_password_hash(form.password.data or 'defaultpass123')
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'User {user.username} created successfully.', 'success')
            current_app.logger.info(f'User {user.username} created by admin {current_user.username}')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the user. Please try again.', 'error')
            current_app.logger.error(f'Error creating user: {str(e)}')
    
    return render_template('admin/user_form.html', form=form, title='Add User')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserManagementForm(obj=user)
    
    if form.validate_on_submit():
        try:
            user.username = form.username.data
            user.email = form.email.data
            user.full_name = form.full_name.data
            user.phone = form.phone.data
            user.address = form.address.data
            user.role = form.role.data
            
            if form.password.data:
                user.password_hash = generate_password_hash(form.password.data)
            
            db.session.commit()
            
            flash(f'User {user.username} updated successfully.', 'success')
            current_app.logger.info(f'User {user.username} updated by admin {current_user.username}')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the user. Please try again.', 'error')
            current_app.logger.error(f'Error updating user: {str(e)}')
    
    return render_template('admin/user_form.html', form=form, user=user, title='Edit User')

@admin_bp.route('/users/<int:user_id>/toggle-status')
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.username} {status} successfully.', 'success')
        current_app.logger.info(f'User {user.username} {status} by admin {current_user.username}')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the user status. Please try again.', 'error')
        current_app.logger.error(f'Error toggling user status: {str(e)}')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/rescue-teams')
@login_required
@admin_required
def rescue_teams():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    rescue_teams = User.query.filter_by(role='rescue_team')\
                            .order_by(User.created_at.desc())\
                            .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/rescue_teams.html', rescue_teams=rescue_teams)

@admin_bp.route('/resources')
@login_required
@admin_required
def resources():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    resources = Resource.query.order_by(Resource.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/resources.html', resources=resources)

@admin_bp.route('/resources/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_resource():
    form = ResourceForm()
    
    if form.validate_on_submit():
        try:
            resource = Resource(
                name=form.name.data,
                resource_type=form.resource_type.data,
                description=form.description.data,
                availability_status=form.availability_status.data,
                location=form.location.data
            )
            
            db.session.add(resource)
            db.session.commit()
            
            flash(f'Resource {resource.name} created successfully.', 'success')
            current_app.logger.info(f'Resource {resource.name} created by admin {current_user.username}')
            return redirect(url_for('admin.resources'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the resource. Please try again.', 'error')
            current_app.logger.error(f'Error creating resource: {str(e)}')
    
    return render_template('admin/resource_form.html', form=form, title='Add Resource')

@admin_bp.route('/resources/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    form = ResourceForm(obj=resource)
    
    if form.validate_on_submit():
        try:
            resource.name = form.name.data
            resource.resource_type = form.resource_type.data
            resource.description = form.description.data
            resource.availability_status = form.availability_status.data
            resource.location = form.location.data
            
            db.session.commit()
            
            flash(f'Resource {resource.name} updated successfully.', 'success')
            current_app.logger.info(f'Resource {resource.name} updated by admin {current_user.username}')
            return redirect(url_for('admin.resources'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the resource. Please try again.', 'error')
            current_app.logger.error(f'Error updating resource: {str(e)}')
    
    return render_template('admin/resource_form.html', form=form, resource=resource, title='Edit Resource')

@admin_bp.route('/incidents')
@login_required
@admin_required
def incidents():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    
    query = Incident.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    
    incidents = query.order_by(Incident.created_at.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/incidents.html', 
                         incidents=incidents,
                         status_filter=status_filter,
                         priority_filter=priority_filter)

@admin_bp.route('/incidents/<int:incident_id>')
@login_required
@admin_required
def view_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    status_updates = incident.status_updates.order_by(db.desc('created_at')).all()
    
    # Get available rescue teams and resources for assignment
    rescue_teams = User.query.filter_by(role='rescue_team', is_active=True).all()
    available_resources = Resource.query.filter_by(availability_status='available').all()
    
    # Forms for assignments
    assign_team_form = AssignTeamForm()
    assign_team_form.team_id.choices = [(t.id, f"{t.full_name} ({t.username})") for t in rescue_teams]
    
    assign_resource_form = AssignResourceForm()
    assign_resource_form.resource_id.choices = [(r.id, f"{r.name} ({r.resource_type})") for r in available_resources]
    
    status_form = StatusUpdateForm()
    
    return render_template('admin/incident_details.html',
                         incident=incident,
                         status_updates=status_updates,
                         assign_team_form=assign_team_form,
                         assign_resource_form=assign_resource_form,
                         status_form=status_form)

@admin_bp.route('/incidents/<int:incident_id>/assign-team', methods=['POST'])
@login_required
@admin_required
def assign_team(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    form = AssignTeamForm()
    
    # Populate choices
    rescue_teams = User.query.filter_by(role='rescue_team', is_active=True).all()
    form.team_id.choices = [(t.id, f"{t.full_name} ({t.username})") for t in rescue_teams]
    
    if form.validate_on_submit():
        try:
            old_team = incident.assigned_team
            incident.assigned_team_id = form.team_id.data
            
            # Create status update
            team = User.query.get(form.team_id.data)
            notes = form.notes.data or f"Assigned to rescue team: {team.full_name}"
            
            status_update = StatusUpdate(
                incident_id=incident.id,
                old_status=incident.status,
                new_status=incident.status,
                notes=notes,
                updated_by=current_user.id
            )
            
            db.session.add(status_update)
            db.session.commit()
            
            flash(f'Incident assigned to {team.full_name} successfully.', 'success')
            current_app.logger.info(f'Incident {incident.id} assigned to team {team.username} by admin {current_user.username}')
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while assigning the team. Please try again.', 'error')
            current_app.logger.error(f'Error assigning team: {str(e)}')
    
    return redirect(url_for('admin.view_incident', incident_id=incident_id))

@admin_bp.route('/incidents/<int:incident_id>/assign-resource', methods=['POST'])
@login_required
@admin_required
def assign_resource(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    form = AssignResourceForm()
    
    # Populate choices
    available_resources = Resource.query.filter_by(availability_status='available').all()
    form.resource_id.choices = [(r.id, f"{r.name} ({r.resource_type})") for r in available_resources]
    
    if form.validate_on_submit():
        try:
            resource = Resource.query.get(form.resource_id.data)
            
            # Check if resource is already assigned to this incident
            existing_assignment = IncidentResource.query.filter_by(
                incident_id=incident.id,
                resource_id=resource.id,
                released_at=None
            ).first()
            
            if existing_assignment:
                flash('This resource is already assigned to this incident.', 'warning')
                return redirect(url_for('admin.view_incident', incident_id=incident_id))
            
            # Create resource assignment
            assignment = IncidentResource(
                incident_id=incident.id,
                resource_id=resource.id,
                notes=form.notes.data
            )
            
            # Update resource status
            resource.availability_status = 'in_use'
            
            # Create status update
            notes = form.notes.data or f"Resource assigned: {resource.name}"
            status_update = StatusUpdate(
                incident_id=incident.id,
                old_status=incident.status,
                new_status=incident.status,
                notes=notes,
                updated_by=current_user.id
            )
            
            db.session.add(assignment)
            db.session.add(status_update)
            db.session.commit()
            
            flash(f'Resource {resource.name} assigned successfully.', 'success')
            current_app.logger.info(f'Resource {resource.name} assigned to incident {incident.id} by admin {current_user.username}')
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while assigning the resource. Please try again.', 'error')
            current_app.logger.error(f'Error assigning resource: {str(e)}')
    
    return redirect(url_for('admin.view_incident', incident_id=incident_id))

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    return render_template('admin/analytics.html')

@admin_bp.route('/api/analytics-data')
@login_required
@admin_required
def analytics_data():
    # Incidents by status
    status_data = db.session.query(
        Incident.status,
        func.count(Incident.id)
    ).group_by(Incident.status).all()
    
    # Incidents by type
    type_data = db.session.query(
        Incident.incident_type,
        func.count(Incident.id)
    ).group_by(Incident.incident_type).all()
    
    # Incidents by priority
    priority_data = db.session.query(
        Incident.priority,
        func.count(Incident.id)
    ).group_by(Incident.priority).all()
    
    # Monthly incident trends (last 12 months)
    monthly_data = db.session.query(
        extract('year', Incident.created_at).label('year'),
        extract('month', Incident.created_at).label('month'),
        func.count(Incident.id).label('count')
    ).group_by('year', 'month').order_by('year', 'month').limit(12).all()
    
    return jsonify({
        'status_distribution': {
            'labels': [item[0].title() for item in status_data],
            'data': [item[1] for item in status_data]
        },
        'type_distribution': {
            'labels': [item[0].replace('_', ' ').title() for item in type_data],
            'data': [item[1] for item in type_data]
        },
        'priority_distribution': {
            'labels': [item[0].title() for item in priority_data],
            'data': [item[1] for item in priority_data]
        },
        'monthly_trends': {
            'labels': [f"{int(item[1])}/{int(item[0])}" for item in monthly_data],
            'data': [item[2] for item in monthly_data]
        }
    })
