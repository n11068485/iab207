import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from .models import Event, Order, Comment
from .forms import EventForm, BookingForm, CommentForm
from . import db

main_bp = Blueprint('main', __name__)


SECTORS = [
    'Technology', 'Finance & Banking', 'Engineering', 'Healthcare',
    'Law', 'Creative Industries', 'Consulting', 'Government & Public Policy',
    'Education', 'Other'
]


@main_bp.route('/')
def index():
    sector = request.args.get('sector', '').strip()
    search = request.args.get('search', '').strip()

    query = db.select(Event)
    if sector:
        query = query.where(Event.sector == sector)
    if search:
        query = query.where(Event.title.ilike(f'%{search}%'))
    query = query.order_by(Event.date)

    events = db.session.scalars(query).all()
    return render_template('index.html', events=events, sectors=SECTORS,
                           selected_sector=sector, search=search)


@main_bp.route('/event/<int:id>')
def event_detail(id):
    event = db.get_or_404(Event, id)
    comment_form = CommentForm()
    return render_template('event-detail.html', event=event, comment_form=comment_form)


@main_bp.route('/event/<int:id>/book', methods=['GET'])
@login_required
def book_event_page(id):
    event = db.get_or_404(Event, id)
    if event.status != 'Open' or event.tickets_remaining == 0:
        flash('Tickets are not available for this event.', 'danger')
        return redirect(url_for('main.event_detail', id=id))
    form = BookingForm()
    return render_template('book-event.html', event=event, form=form)


@main_bp.route('/bookings')
@login_required
def booking_history():
    orders = db.session.scalars(
        db.select(Order).where(Order.user_id == current_user.id)
        .order_by(Order.booked_at.desc())
    ).all()
    now = datetime.now()
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


@main_bp.route('/event/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = db.get_or_404(Event, id)
    if event.user_id != current_user.id:
        abort(403)

    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.end_time = form.end_time.data
        event.venue = form.venue.data
        event.city = form.city.data
        event.sector = form.sector.data
        event.subsector = form.subsector.data or ''
        event.ticket_capacity = form.ticket_capacity.data
        event.ticket_price = form.ticket_price.data
        event.aoc_level = form.aoc_level.data
        event.aoc_country_name = form.aoc_country_name.data
        event.aoc_custom_text = form.aoc_custom_text.data

        img_file = form.image.data
        if img_file and img_file.filename:
            ext = os.path.splitext(img_file.filename)[1].lower()
            filename = uuid.uuid4().hex + ext
            upload_dir = os.path.join(current_app.root_path, 'static', 'img')
            img_file.save(os.path.join(upload_dir, filename))
            event.image = filename

        db.session.commit()
        flash('Event updated successfully.', 'success')
        return redirect(url_for('main.event_detail', id=id))

    return render_template('create-event.html', form=form, edit=True)


@main_bp.route('/event/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_event(id):
    event = db.get_or_404(Event, id)
    if event.user_id != current_user.id:
        abort(403)
    event.status = 'Cancelled'
    db.session.commit()
    flash('Event has been cancelled.', 'success')
    return redirect(url_for('main.event_detail', id=id))


@main_bp.route('/event/<int:id>/book', methods=['POST'])
@login_required
def book_event(id):
    event = db.get_or_404(Event, id)
    form = BookingForm()
    if not form.validate_on_submit():
        return render_template('book-event.html', event=event, form=form)

    if event.status != 'Open':
        flash('This event is no longer accepting bookings.', 'danger')
        return redirect(url_for('main.event_detail', id=id))

    qty = form.quantity.data
    if qty > event.tickets_remaining:
        flash(f'Only {event.tickets_remaining} ticket(s) remaining.', 'danger')
        return redirect(url_for('main.event_detail', id=id))

    order = Order(
        order_ref='',
        quantity=qty,
        unit_price=event.ticket_price,
        total_price=event.ticket_price * qty,
        user_id=current_user.id,
        event_id=event.id
    )
    db.session.add(order)
    db.session.flush()
    order.order_ref = f"NXN-{datetime.now().year}-{order.id:05d}"

    event.tickets_remaining -= qty
    if event.tickets_remaining == 0:
        event.status = 'Sold Out'

    db.session.commit()
    flash(f'Booking confirmed! Your order ID is {order.order_ref}.', 'success')
    return redirect(url_for('main.booking_history'))


@main_bp.route('/event/<int:id>/comment', methods=['POST'])
@login_required
def post_comment(id):
    flash('Comments coming soon.', 'info')
    return redirect(url_for('main.event_detail', id=id))
