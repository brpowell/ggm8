from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Create association tables for many-to-many relationships
company_person = db.Table('company_person',
    db.Column('company_id', db.Integer, db.ForeignKey('companies.id')),
    db.Column('person_id', db.Integer, db.ForeignKey('people.id'))
)
developer_game = db.Table('developer_game',
    db.Column('company_id', db.Integer, db.ForeignKey('companies.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'))
)
publisher_game = db.Table('publisher_game',
    db.Column('company_id', db.Integer, db.ForeignKey('companies.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'))
)
person_game = db.Table('person_game',
    db.Column('person_id', db.Integer, db.ForeignKey('people.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'))
)
worked_with = db.Table('worked_with',
    db.Column('person_id', db.Integer, db.ForeignKey('people.id')),
    db.Column('coworker_id', db.Integer, db.ForeignKey('people.id'))
)
game_platform = db.Table('game_platform',
    db.Column('game_id', db.Integer, db.ForeignKey('games.id')),
    db.Column('platform_id', db.Integer, db.ForeignKey('platforms.id'))
)


class Rating(db.Model):
    __tablename__= 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'))
    metacritic = db.Column(db.Integer)

    def __repr__(self):
        return '<Rating %r>' % self.name


class Platform(db.Model):
    __tablename__ = 'platforms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    short = db.Column(db.String(10))
    ratings = db.relationship('Rating', backref='platform')

    def best_rating():
        r_iter = iter(ratings)
        best = next(r_iter)
        for r in r_iter:
            if r.metacritic > best.metacritic:
                best = r
        return best

    def __repr__(self):
        return '<Platform %r>' % self.name


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    deck = db.Column(db.String(255))
    image = db.Column(db.String(255))
    release_date = db.Column(db.DateTime)
    platforms = db.relationship('Platform', secondary=game_platform,
                    backref=db.backref('games', lazy='dynamic'))
    ratings = db.relationship('Rating', backref='game')
    first_for = db.relationship('Game', backref='first_game')

    def best_rating():
        r_iter = iter(ratings)
        best = next(r_iter)
        for r in r_iter:
            if r.metacritic > best.metacritic:
                best = r
        return best

    def __repr__(self):
        return '<Game %r>' % self.name


class Person(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    image = db.Column(db.String(255))
    hometown = db.Column(db.String(255))
    country = db.Column(db.String(255))
    birth_date = db.Column(db.DateTime)
    death_date = db.Column(db.DateTime)
    deck = db.Column(db.String(255))
    first_credited_game = db.Column(db.Integer, db.ForeignKey('games.id'))

    games = db.relationship('Game', secondary=person_game,
                        backref=db.backref('people', lazy='dynamic'))
    people = db.relationship('Person', secondary=worked_with,
                        backref=db.backref('people', lazy='dynamic'))

    def coworkers(self, person):
        self.people.append(person)
        person.people.append(self)
        db.session.add(self)
        db.session.add(person)
        db.session.commit()

    def __repr__(self):
        return '<Person %r>' % self.name


class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    image = db.Column(db.String(255))
    city = db.Column(db.String(255))
    country = db.Column(db.String(255))
    deck = db.Column(db.Text)
    date_founded = db.Column(db.DateTime)
    people = db.relationship('Person', secondary=company_person,
                        backref=db.backref('companies', lazy='dynamic'))
    developed_games = db.relationship('Game', secondary=developer_game,
                        backref=db.backref('developers', lazy='dynamic'))
    published_games = db.relationship('Game', secondary=publisher_game,
                        backref=db.backref('publishers', lazy='dynamic'))

    def __repr__(self):
        return '<Company %r>' % self.name