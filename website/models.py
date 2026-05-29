from . import db
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(200), nullable=False)

    # relationships
    events = db.relationship('Event', back_populates='creator', lazy=True)
    orders = db.relationship('Order', back_populates='user', lazy=True)
    comments = db.relationship('Comment', back_populates='user', lazy=True)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(400), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(200), nullable=False)
    venue_address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(100), nullable=False)
    subsector = db.Column(db.String(100), nullable=True)
    ticket_capacity = db.Column(db.Integer, nullable=False)
    tickets_remaining = db.Column(db.Integer, nullable=False)
    ticket_price = db.Column(db.Float, nullable=False)
    # Open, Inactive, Sold Out, Cancelled
    status = db.Column(db.String(20), nullable=False, default='Open')
    # none, generic, enhanced
    aoc_level = db.Column(db.String(10), nullable=False, default='none')
    aoc_country_name = db.Column(db.String(200), nullable=True)
    aoc_custom_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # foreign key to creator
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    creator = db.relationship('User', back_populates='events')
    orders = db.relationship('Order', back_populates='event', lazy=True)
    comments = db.relationship('Comment', back_populates='event',
                               lazy=True, order_by='Comment.posted_at')


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    # e.g. NXN-2025-00147
    order_ref = db.Column(db.String(20), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.now)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    # relationships
    user = db.relationship('User', back_populates='orders')
    event = db.relationship('Event', back_populates='orders')


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.now)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    # relationships
    user = db.relationship('User', back_populates='comments')
    event = db.relationship('Event', back_populates='comments')
