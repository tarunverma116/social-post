from datetime import datetime
from model.users import db


class Post(db.Model):
    __tablename__ = "posts"

    # 🔹 Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # 🔹 Post Content
    content = db.Column(db.Text, nullable=False)

    # 🔹 Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔹 Foreign Key (User who created post)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 🔥 Relationship (VERY IMPORTANT)
    user = db.relationship("Users", backref="posts")

    def __repr__(self):
        return f"<Post {self.id} by User {self.user_id}>"