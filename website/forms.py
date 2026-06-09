from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields import (TextAreaField, SubmitField, StringField,
                             PasswordField, SelectField, IntegerField,
                             FloatField, DateTimeLocalField)
from wtforms.validators import (InputRequired, Length, Email, EqualTo,
                                 NumberRange, Optional)


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        InputRequired(), Email('Please enter a valid email')])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        InputRequired(), Length(min=2, max=50)])
    surname = StringField('Surname', validators=[
        InputRequired(), Length(min=2, max=50)])
    email = StringField('Email Address', validators=[
        InputRequired(), Email('Please enter a valid email')])
    contact_number = StringField('Contact Number', validators=[
        InputRequired(), Length(min=8, max=20)])
    street_address = StringField('Street Address', validators=[
        InputRequired(), Length(min=5, max=200)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=6),
        EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Register')


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[
        InputRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[InputRequired()])
    image = FileField('Event Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only')])
    date = DateTimeLocalField('Start Date & Time', format='%Y-%m-%dT%H:%M',
                              validators=[InputRequired()])
    end_time = DateTimeLocalField('End Date & Time', format='%Y-%m-%dT%H:%M',
                                  validators=[InputRequired()])
    venue = StringField('Venue Name', validators=[
        InputRequired(), Length(max=200)])
    venue_address = StringField('Venue Street Address', validators=[
        InputRequired(), Length(max=300)])
    state = SelectField('State / Territory', choices=[
        ('Queensland', 'Queensland'),
        ('New South Wales', 'New South Wales'),
        ('Victoria', 'Victoria'),
        ('Western Australia', 'Western Australia'),
        ('South Australia', 'South Australia'),
        ('Australian Capital Territory', 'Australian Capital Territory'),
        ('Tasmania', 'Tasmania'),
        ('Northern Territory', 'Northern Territory'),
    ], validators=[InputRequired()])
    city = StringField('City / Council Area', validators=[
        InputRequired(), Length(max=100)])
    sector = SelectField('Sector', choices=[
        ('Technology', 'Technology'), ('Finance & Banking', 'Finance & Banking'),
        ('Engineering', 'Engineering'), ('Healthcare', 'Healthcare'),
        ('Law', 'Law'), ('Creative Industries', 'Creative Industries'),
        ('Consulting', 'Consulting'), ('Government & Public Policy',
        'Government & Public Policy'), ('Education', 'Education'),
        ('Other', 'Other')])
    subsector = StringField('Subsector', validators=[Optional(), Length(max=100)])
    ticket_capacity = IntegerField('Ticket Capacity', validators=[
        InputRequired(), NumberRange(min=1)])
    ticket_price = FloatField('Ticket Price (AUD)', validators=[
        InputRequired(), NumberRange(min=0)])
    aoc_level = SelectField('Acknowledgement of Country', choices=[
        ('none', 'None'), ('generic', 'Generic'), ('enhanced', 'Enhanced')])
    aoc_country_name = StringField('Country Name', validators=[
        Optional(), Length(max=200)])
    aoc_custom_text = TextAreaField('Custom Acknowledgement Text',
                                    validators=[Optional()])
    submit = SubmitField('Submit Event for Review')


class BookingForm(FlaskForm):
    quantity = IntegerField('Number of Tickets', validators=[
        InputRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Confirm Booking')


class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[
        InputRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Post Comment')
