from fastapi_users.db import SQLAlchemyBaseUserTable
from fastapi_users.db.sqlalchemy import GUID
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    Enum,
    select,
    func,
)
from sqlalchemy.orm import relationship, column_property, backref
from app.database import Base
from redis_conf.redis import redis_pub
from app.users.enums import Gender
from sqlalchemy import text


user_achievements_association = Table(
    'user-achievements',
    Base.metadata,
    Column('User_id', GUID, ForeignKey('Users.id')),
    Column('Achievement_id', Integer, ForeignKey('Achievements.id')),
)

user_courses_association = Table(
    'user-courses',
    Base.metadata,
    Column('User_id', GUID, ForeignKey('Users.id')),
    Column('Course_id', Integer, ForeignKey('Courses.id')),
)

graduated_user_courses_association = Table(
    'user-courses-graduated',
    Base.metadata,
    Column('User_id', GUID, ForeignKey('Users.id')),
    Column('Course_id', Integer, ForeignKey('Courses.id')),
)


class User(Base, SQLAlchemyBaseUserTable):
    __tablename__ = 'Users'
    id = Column(GUID, primary_key=True, index=True)
    avatar = relationship(
        "Avatar",
        lazy='joined',
        uselist=False,
        backref=backref("user_avatar", uselist=False),
    )
    username = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    description = Column(Text)
    website = Column(String(50), nullable=True)
    phone = Column(String(15), nullable=True)
    gender = Column(Enum(Gender), default=None, nullable=True)
    birth_date = Column(DateTime)
    achievements = relationship(
        'Achievement',
        secondary=user_achievements_association,
        backref='users',
        lazy='select',
    )
    subscribed_courses = relationship(
        'Course',
        secondary=user_courses_association,
        backref='subscribers',
        lazy='select',
    )
    graduated_courses = relationship(
        'Course',
        secondary=graduated_user_courses_association,
        backref='graduated_users',
        lazy='select',
    )
    is_active = Column(Boolean, default=True)
    is_author = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    hashed_password = Column(Text, nullable=False)
    is_superuser = Column(Boolean, default=False)
    courses = relationship('Course', back_populates='user')
    files = relationship('File', backref='added_by')
    sold_courses = Column(Integer, default=0)
    following = relationship(
        'User',
        lambda: user_following,
        primaryjoin=lambda: User.id == user_following.c.user_id,
        secondaryjoin=lambda: User.id == user_following.c.following_id,
        backref='followers',
    )
    courses_count = column_property(
        select(
            text('count(*) from "Courses" where "Courses".user_id="Users".id')
        ).scalar_subquery()
    )

    def __init__(
        self,
        id: int,
        username: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        email: str,
        is_superuser: bool,
    ):
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_superuser = is_superuser
        self.is_followed = False

    def __str__(self):
        return self.username

    def __repr__(self):
        return '<User {0}>'.format(self)

    @property
    def is_followed(self):
        return self._is_followed

    @is_followed.setter
    def is_followed(self, value):
        self._is_followed = value

    @property
    def posts_count(self):
        count = redis_pub.hget(f"user:{self.id}", "posts_count")
        if count:
            return int(count)
        return 0

    @property
    def followers_count(self):
        count = redis_pub.hget(f"user:{self.id}", "followers_count")
        if count:
            return int(count)
        return 0

    @property
    def following_count(self):
        count = redis_pub.hget(f"user:{self.id}", "following_count")
        if count:
            return int(count)
        return 0


user_following = Table(
    'user_following',
    Base.metadata,
    Column('user_id', GUID, ForeignKey(User.id), primary_key=True),
    Column('following_id', GUID, ForeignKey(User.id), primary_key=True),
)
