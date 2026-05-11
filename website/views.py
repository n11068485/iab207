from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/event')
def event_detail():
    return render_template('event-detail.html')


@main_bp.route('/bookings')
def booking_history():
    return render_template('booking-history.html')


@main_bp.route('/create')
def create_event():
    return render_template('create-event.html')
