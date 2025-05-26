from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from models import Incident, StatusUpdate
from forms import StatusUpdateForm
from utils import rescue_team_required
from . import rescue_bp

@rescue_bp.route('/dashboard')
@login_required
@rescue_team_required
def dashboard():
    # Get assigned incidents
    assigned_incidents = Incident.query.filter_by(assigned_team_id=current_user.id)\
                                      .order_by(Incident.created_at.desc())\
                                      .limit(10).all()
    
    # Get all unassigned incidents
    unassigned_incidents = Incident.query.filter_by(assigned_team_id=None)\
                                        .filter(Incident.status.in_(['pending', 'in_progress']))\
                                        .order_by(Incident.created_at.desc())\
                                        .limit(5).all()
    
    # Get statistics
    total_assigned = Incident.query.filter_by(assigned_team_id=current_user.id).count()
    pending_assigned = Incident.query.filter_by(assigned_team_id=current_user.id, status='pending').count()
    in_progress_assigned = Incident.query.filter_by(assigned_team_id=current_user.id, status='in_progress').count()
    resolved_assigned = Incident.query.filter_by(assigned_team_id=current_user.id, status='resolved').count()
    
    stats = {
        'total_assigned': total_assigned,
        'pending': pending_assigned,
        'in_progress': in_progress_assigned,
        'resolved': resolved_assigned
    }
    
    return render_template('rescue/dashboard.html',
                         assigned_incidents=assigned_incidents,
                         unassigned_incidents=unassigned_incidents,
                         stats=stats)

@rescue_bp.route('/incident/<int:incident_id>')
@login_required
@rescue_team_required
def incident_details(incident_id):
    # Rescue teams can view any incident, but can only update assigned ones
    incident = Incident.query.get_or_404(incident_id)
    
    # Get status updates for this incident
    status_updates = incident.status_updates.order_by(db.desc('created_at')).all()
    
    # Check if this incident is assigned to current user
    can_update = incident.assigned_team_id == current_user.id
    
    form = StatusUpdateForm() if can_update else None
    
    return render_template('rescue/incident_details.html',
                         incident=incident,
                         status_updates=status_updates,
                         can_update=can_update,
                         form=form)

@rescue_bp.route('/incident/<int:incident_id>/update-status', methods=['POST'])
@login_required
@rescue_team_required
def update_status(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    
    # Check if incident is assigned to current user
    if incident.assigned_team_id != current_user.id:
        flash('You can only update incidents assigned to you.', 'error')
        return redirect(url_for('rescue.incident_details', incident_id=incident_id))
    
    form = StatusUpdateForm()
    if form.validate_on_submit():
        try:
            old_status = incident.status
            new_status = form.status.data
            
            # Create status update record
            status_update = StatusUpdate(
                incident_id=incident.id,
                old_status=old_status,
                new_status=new_status,
                notes=form.notes.data,
                updated_by=current_user.id
            )
            
            # Update incident status
            incident.status = new_status
            
            db.session.add(status_update)
            db.session.commit()
            
            flash(f'Incident status updated from "{old_status}" to "{new_status}".', 'success')
            current_app.logger.info(f'Incident {incident.id} status updated by {current_user.username}: {old_status} -> {new_status}')
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the status. Please try again.', 'error')
            current_app.logger.error(f'Error updating incident status: {str(e)}')
    
    return redirect(url_for('rescue.incident_details', incident_id=incident_id))

@rescue_bp.route('/accept-incident/<int:incident_id>')
@login_required
@rescue_team_required
def accept_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    
    # Check if incident is unassigned
    if incident.assigned_team_id is not None:
        flash('This incident is already assigned to a team.', 'warning')
        return redirect(url_for('rescue.dashboard'))
    
    try:
        # Assign incident to current user
        incident.assigned_team_id = current_user.id
        if incident.status == 'pending':
            incident.status = 'in_progress'
        
        # Create status update record
        status_update = StatusUpdate(
            incident_id=incident.id,
            old_status='pending',
            new_status='in_progress',
            notes=f'Incident accepted by rescue team {current_user.full_name}',
            updated_by=current_user.id
        )
        
        db.session.add(status_update)
        db.session.commit()
        
        flash(f'You have accepted incident: {incident.title}', 'success')
        current_app.logger.info(f'Incident {incident.id} accepted by {current_user.username}')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while accepting the incident. Please try again.', 'error')
        current_app.logger.error(f'Error accepting incident: {str(e)}')
    
    return redirect(url_for('rescue.incident_details', incident_id=incident_id))

@rescue_bp.route('/my-incidents')
@login_required
@rescue_team_required
def my_incidents():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    incidents = Incident.query.filter_by(assigned_team_id=current_user.id)\
                             .order_by(Incident.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('rescue/my_incidents.html', incidents=incidents)
