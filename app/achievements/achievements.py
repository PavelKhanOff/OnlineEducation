from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi_users import models as fastapi_model
from http import HTTPStatus
from starlette.responses import Response

from . import models, schemas
from app.auth.auth import fastapi_users
from app.pagination import CustomPage as Page
from elastic import es

from app.achievements.achievement_dal import AchievementDAL
from app.achievements.dependencies import get_achievement_dal


router = APIRouter(tags=['Achievements'])


@router.get(
    '/core/achievements', response_model=Page[schemas.AchievementOut], status_code=200
)
async def show_achievements(
    achievement_dal: AchievementDAL = Depends(get_achievement_dal),
    title: Optional[str] = None,
):
    achievements = await achievement_dal.get_all_query()
    if title:
        achievements = await achievement_dal.get_by_title_query(title)

    return await paginate(achievement_dal.db_session, achievements)


@router.post('/core/achievement/create', status_code=201)
async def create_achievement(
    request: schemas.Achievement,
    user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(superuser=True)
    ),
    achievement_dal: AchievementDAL = Depends(get_achievement_dal),
):
    new_achievement = await achievement_dal.create_achievement(request)
    if not new_achievement:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Такое достижение уже существует"},
        )
    try:
        doc = {
            "title": new_achievement.title,
            "description": new_achievement.description,
        }
        await es.index("achievements", id=new_achievement.id, body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return new_achievement


@router.patch('/core/achievement/{achievement_id}/update', status_code=202)
async def update_achievement(
    achievement_id: int,
    request: schemas.UpdateAchievement,
    user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(superuser=True)
    ),
    achievement_dal: AchievementDAL = Depends(get_achievement_dal),
):
    if await achievement_dal.get_by_title(request.title):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Такое достижение уже существует"},
        )
    achievement = await achievement_dal.get_by_id(achievement_id)
    if not achievement:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Достижение не найдено"},
        )
    await achievement_dal.update_achievement(
        achievement_id, request.dict(exclude_unset=True)
    )
    try:
        doc = {"title": achievement.title, "description": achievement.description}
        await es.index("achievements", id=achievement_id, body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return achievement


@router.delete('/core/achievement/{achievement_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_achievement(
    achievement_id: int,
    user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(superuser=True)
    ),
    achievement_dal: AchievementDAL = Depends(get_achievement_dal),
):
    achievement = await achievement_dal.check_by_id(achievement_id)
    if not achievement:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Достижение не найдено"},
        )
    await achievement_dal.delete_achievement(achievement_id)
    try:
        await es.delete(index="achievements", id=achievement_id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    try:
        doc = {
            "script": {
                "source": "if (ctx._source.achievements.contains(params.achievement)) { ctx._source.achievements.remove(ctx._source.achievements.indexOf(achievement.tag)) }",
                "lang": "painless",
                "params": {"achievement": achievement_id},
            },
            "query": {"match": {"achievements": achievement_id}},
        }
        await es.update_by_query("users", body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return Response(status_code=204)


@router.post('/core/achievement', status_code=200)
async def bound_or_unbound_user_achievement(
    request: schemas.UserAchievement,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    achievement_dal: AchievementDAL = Depends(get_achievement_dal),
):
    checker = await achievement_dal.achievement(user.id, request.achievements_id)
    try:
        if checker:
            body_script = {
                "script": {
                    "source": "ctx._source.achievements.add(params.achievement)",
                    "lang": "painless",
                    "params": {"achievement": request.achievements_id},
                }
            }
        else:
            body_script = {
                "script": {
                    "source": "if (ctx._source.achievements.contains(params.achievement)) { ctx._source.achievements.remove(ctx._source.achievements.indexOf(params.achievement)) }",
                    "lang": "painless",
                    "params": {"achievement": request.achievements_id},
                }
            }

        await es.update("users", id=user.id, body=body_script)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return JSONResponse(content={"message": "ОК"})
