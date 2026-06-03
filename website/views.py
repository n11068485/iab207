import os
import re
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request, abort
from flask_login import login_required, current_user
from .models import Event, Order, Comment
from .forms import EventForm, BookingForm, CommentForm
from . import db

main_bp = Blueprint('main', __name__)


def save_event_image(img_file):
    # uuid hex ensures no filename collisions across uploads
    ext = os.path.splitext(img_file.filename)[1].lower()
    filename = uuid.uuid4().hex + ext
    img_file.save(os.path.join(current_app.root_path, 'static', 'img', filename))
    return filename


def delete_event_image(filename):
    if not filename:
        return
    # seed images use descriptive names (e.g. tech-summit.jpeg), not uuid hex.
    # this guard ensures only user-uploaded files are deleted on image replacement.
    if not re.match(r'^[0-9a-f]{32}\.[a-z]+$', filename):
        return
    filepath = os.path.join(current_app.root_path, 'static', 'img', filename)
    if os.path.exists(filepath):
        os.remove(filepath)


@main_bp.route('/')
def index():
    state  = request.args.get('state', '')
    city   = request.args.get('city', '')
    sector = request.args.get('sector', '')
    search = request.args.get('search', '')

    query = db.select(Event).order_by(Event.date)
    if state:
        query = query.where(Event.state == state)
    if city:
        query = query.where(Event.city == city)
    if sector:
        query = query.where(Event.sector == sector)
    if search:
        query = query.where(
            db.or_(Event.title.ilike(f'%{search}%'),
                   Event.description.ilike(f'%{search}%'))
        )

    events  = db.session.scalars(query).all()
    sectors = sorted(set(db.session.scalars(db.select(Event.sector)).all()))
    states  = sorted(set(db.session.scalars(db.select(Event.state)).all()))
    # when a state is selected the city list narrows to only cities in that state,
    # giving a server-side cascade without javascript.
    city_q = db.select(Event.city)
    if state:
        city_q = city_q.where(Event.state == state)
    cities = sorted(set(db.session.scalars(city_q).all()))

    return render_template('index.html', events=events,
                           sectors=sectors, states=states, cities=cities,
                           selected_state=state, selected_city=city,
                           selected_sector=sector, search=search)


@main_bp.route('/event/<int:id>')
def event_detail(id):
    event = db.get_or_404(Event, id)
    comment_form = CommentForm()
    return render_template('event-detail.html', event=event, comment_form=comment_form)


@main_bp.route('/event/<int:id>/comment', methods=['POST'])
@login_required
def post_comment(id):
    event = db.get_or_404(Event, id)
    form = CommentForm()
    if form.validate_on_submit():
        db.session.add(Comment(
            text=form.text.data,
            user_id=current_user.id,
            event_id=event.id
        ))
        db.session.commit()
    return redirect(url_for('main.event_detail', id=event.id))


@main_bp.route('/event/<int:id>/book', methods=['GET'])
@login_required
def book_event_page(id):
    event = db.get_or_404(Event, id)
    if event.status != 'Open':
        flash('This event is not available for booking.', 'danger')
        return redirect(url_for('main.event_detail', id=event.id))
    return render_template('book-event.html', event=event, form=BookingForm())


@main_bp.route('/event/<int:id>/book', methods=['POST'])
@login_required
def book_event(id):
    event = db.get_or_404(Event, id)
    if event.status != 'Open':
        flash('This event is not available for booking.', 'danger')
        return redirect(url_for('main.event_detail', id=event.id))

    form = BookingForm()
    if form.validate_on_submit():
        qty = form.quantity.data
        if qty > event.tickets_remaining:
            flash(f'Only {event.tickets_remaining} ticket(s) remaining.', 'danger')
            return render_template('book-event.html', event=event, form=form)

        now = datetime.now()
        order = Order(
            order_ref='_',
            quantity=qty,
            unit_price=event.ticket_price,
            total_price=round(qty * event.ticket_price, 2),
            booked_at=now,
            user_id=current_user.id,
            event_id=event.id
        )
        db.session.add(order)
        # flush assigns the db-generated id without committing, so it's
        # available to format the order reference before the final commit.
        db.session.flush()
        order.order_ref = f"NXN-{now.year}-{order.id:05d}"

        event.tickets_remaining -= qty
        if event.tickets_remaining == 0:
            event.status = 'Sold Out'

        db.session.commit()
        flash(f'Booking confirmed! Reference: {order.order_ref}', 'success')
        return redirect(url_for('main.booking_history'))

    return render_template('book-event.html', event=event, form=form)


@main_bp.route('/bookings')
@login_required
def booking_history():
    now = datetime.now()
    # uses the relationship attribute rather than a fresh query because
    # flask-login already has the user loaded; avoids a redundant db round trip.
    orders = sorted(current_user.orders, key=lambda o: o.event.date)
    upcoming = [o for o in orders if o.event.date >= now]
    past = [o for o in orders if o.event.date < now]
    return render_template('booking-history.html', upcoming=upcoming, past=past)


@main_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        img_file = form.image.data
        if not img_file or not img_file.filename:
            flash('Please upload an event image.', 'danger')
            return render_template('create-event.html', form=form)

        filename = save_event_image(img_file)

        event = Event(
            title=form.title.data,
            description=form.description.data,
            image=filename,
            date=form.date.data,
            end_time=form.end_time.data,
            venue=form.venue.data,
            venue_address=form.venue_address.data,
            city=form.city.data,
            state=form.state.data,
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


@main_bp.route('/event/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = db.get_or_404(Event, id)
    if event.user_id != current_user.id:
        abort(403)

    form = EventForm(obj=event)
    if form.validate_on_submit():
        img_file = form.image.data
        if img_file and img_file.filename:
            # old image is removed before the new one is saved to prevent
            # orphaned files accumulating in static/img over repeated edits.
            delete_event_image(event.image)
            event.image = save_event_image(img_file)

        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.end_time = form.end_time.data
        event.venue = form.venue.data
        event.venue_address = form.venue_address.data
        event.city = form.city.data
        event.state = form.state.data
        event.sector = form.sector.data
        event.subsector = form.subsector.data or ''
        event.ticket_capacity = form.ticket_capacity.data
        event.ticket_price = form.ticket_price.data
        event.aoc_level = form.aoc_level.data
        event.aoc_country_name = form.aoc_country_name.data
        event.aoc_custom_text = form.aoc_custom_text.data

        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('main.event_detail', id=event.id))

    return render_template('create-event.html', form=form, edit=True, event=event)


@main_bp.route('/event/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_event(id):
    event = db.get_or_404(Event, id)
    if event.user_id != current_user.id:
        abort(403)
    event.status = 'Cancelled'
    db.session.commit()
    flash('Event cancelled.', 'success')
    return redirect(url_for('main.event_detail', id=event.id))
