from datetime import datetime
from hashlib import md5

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from twittor import db, login_manager
#記錄follow關係,沒定義class是因為是表示外來物件的關係
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
    )
#記錄帳號資訊
class User(UserMixin, db.Model): #大寫User是class, 小寫user是實例(db的表)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(120)) #增加數據庫記得做 migration
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    tweets = db.relationship('Tweet', backref='author', lazy='dynamic') #一對多

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id), #follow誰
        secondaryjoin=(followers.c.followed_id == id), #被誰follow
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic') #多對多, 是一個 list

    def __repr__(self) -> str: #顯示實例值
        return "id={}, username={}, email={}, password_hash={}".format(
            self.id, self.username, self.email, self.password_hash
        )
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def avatar(self, size=80):
        md5_digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(md5_digest, size)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    def is_following(self, user): #check是否已 follow user
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
        #在followed名單內,followed_id與user.id一致表示已追蹤
        #The “c” is an attribute of SQLAlchemy tables that are not defined as models. For these tables, the table columns are all exposed as sub-attributes of this “c” attribute.

#要讓app_login方法根據id找到用戶
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
#記錄發文推文
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #user_id domain限制於 user表內的 id

    def __repr__(self) -> str:
        return "id={}, body={}, create_time={}, user_id={}".format(
            self.id, self.body, self.create_time, self.user_id
        )