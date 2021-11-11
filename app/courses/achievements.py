from app.users.models import User
from app.achievements.models import Achievement


def get_achievements(user_id, db):
    user = db.query(User).filter(User.id == user_id).first()
    courses = user.courses
    graduated_users = 0
    for course in courses:
        graduated_users += len(course.graduated_users)
    if graduated_users >= 100:
        achievement = db.query(Achievement).filter(Achievement.title == '100 студентов прошли курсы').first()
        user.achievements.append(achievement)
        db.commit()
    if graduated_users >= 1000:
        achievement = db.query(Achievement).filter(Achievement.title == '1000 студентов прошли курсы').first()
        user.achievements.append(achievement)
        db.commit()
    if graduated_users >= 10000:
        achievement = db.query(Achievement).filter(Achievement.title == '10000 студентов прошли курсы').first()
        user.achievements.append(achievement)
        db.commit()
    return 'ok'
