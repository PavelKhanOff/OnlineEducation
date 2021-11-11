async def get_achievements(user_id, middleware_dal):
    courses = await middleware_dal.get_course_with_subs(user_id)
    subscribers = 0
    for i in courses:
        subscribers += len(i.subscribers)
    user = await middleware_dal.get_user_with_achievements(user_id)
    if subscribers >= 100:
        achievement = await middleware_dal.get_by_title('100 студентов на курсах')
        user.achievements.append(achievement)
        middleware_dal.db_session.flush()
    if subscribers >= 1000:
        achievement = await middleware_dal.get_by_title('1000 студентов на курсах')
        user.achievements.append(achievement)
        middleware_dal.db_session.flush()
    if subscribers >= 10000:
        achievement = await middleware_dal.get_by_title('10000 студентов на курсах')
        user.achievements.append(achievement)
        middleware_dal.db_session.flush()
