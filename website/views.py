import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .models import Event
from .forms import EventForm
from . import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    events = db.session.scalars(db.select(Event).order_by(Event.date)).all()
    return render_template('index.html', events=events)


@main_bp.route('/event/<int:id>')
def event_detail(id):
    event = db.get_or_404(Event, id)
    return render_template('event-detail.html', event=event)


@main_bp.route('/bookings')
@login_required
def booking_history():
    return render_template('booking-history.html')


@main_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        img_file = form.image.data
        if not img_file or not img_file.filename:
            flash('Please upload an event image.', 'danger')
            return render_template('create-event.html', form=form)

        ext = os.path.splitext(img_file.filename)[1].lower()
        filename = uuid.uuid4().hex + ext
        upload_dir = os.path.join(current_app.root_path, 'static', 'img')
        img_file.save(os.path.join(upload_dir, filename))

        event = Event(
            title=form.title.data,
            description=form.description.data,
            image=filename,
            date=form.date.data,
            end_time=form.end_time.data,
            venue=form.venue.data,
            city=form.city.data,
            sector=form.sector.data,
            subsector=form.subsector.data or '',
            ticket_capacity=form.ticket_capacity.data,
            tickets_remaining=form.ticket_capacity.data,
            ticket_price=form.ticket_price.data,
            aoc_level=form.aoc_level.data,
            aoc_country_name=form.aoc_country_name.data,
            aoc_custom_text=form.aoc_custom_text.data,
            user_id=current_user.id,
            status='Open'
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('main.event_detail', id=event.id))

    return render_template('create-event.html', form=form)
