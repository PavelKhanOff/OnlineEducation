async def get_achievements(user, file_dal):
    users_files = await file_dal.get_user_files(user_id=user.id, file_type="video")
    if len(users_files) >= 1:
        achievement = await file_dal.get_achievement('1 обучающий ролик')
        user.achievements.append(achievement)
        await file_dal.db_session.flush()
    if len(users_files) >= 10:
        achievement = await file_dal.get_achievement('10 обучающих роликов')
        user.achievements.append(achievement)
        await file_dal.db_session.flush()
    if len(users_files) >= 100:
        achievement = await file_dal.get_achievement('100 обучающих роликов')
        user.achievements.append(achievement)
        await file_dal.db_session.flush()
