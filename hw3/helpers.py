from sqlalchemy import or_, and_

from database_setup import Post, session, User


def allowed_posts(user_id, *args, **kwargs):
    posts = []
    all_posts = session.query(Post, User).filter(
        or_(Post.is_private == False, and_(Post.is_private == True, Post.author_id == user_id))).filter(
        User.id == Post.author_id).filter(Post.author_id == User.id).all()
    for post, user in all_posts:
        posts.append([post.title, post.content, post.image_uuid, user.id, user.name, user.surname])
    return posts
