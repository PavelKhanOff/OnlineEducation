from app.middleware.achievements import get_achievements
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from . import schemas
from .additional_functions import send_subscription_notifications
from .middleware_dal import MiddlewareDAL
from .dependency import get_middleware_dal
from pydantic import UUID4
from app.users.schemas import UserOut
from app.file.schemas import Avatar, Content
from app.file.dependencies import get_file_dal
from app.file.dal import FileDAL
from app.courses.schemas import MyCourseOut
from app.content.dependencies import get_content_dal
from app.content.content_dal import ContentDAL
from app.lessons.schemas import LessonOut


router = APIRouter(tags=['Middleware'])


@router.get('/core/middleware/check_user_exists/{user_id}', status_code=200)
async def check_user(
    user_id: str, middleware_dal: MiddlewareDAL = Depends(get_middleware_dal)
):
    user = await middleware_dal.check_user(user_id)
    if not user:
        return JSONResponse(status_code=200, content={"message": "False"})
    return JSONResponse(status_code=200, content={"message": "True"})


@router.get('/core/middleware/check_superuser_exists/{user_id}', status_code=200)
async def check_user_is_superuser(
    user_id: str, middleware_dal: MiddlewareDAL = Depends(get_middleware_dal)
):
    user = await middleware_dal.get_user(user_id)
    if not user:
        return JSONResponse(
            status_code=200, content={"message": "Пользователь не найден"}
        )
    if not user.is_superuser:
        return JSONResponse(status_code=200, content={"message": "False"})
    return JSONResponse(status_code=200, content={"message": "True"})


@router.get('/core/middleware/check_course_exists/{course_id}', status_code=200)
async def check_course(
    course_id: int,
    middleware_dal: MiddlewareDAL = Depends(get_middleware_dal),
):
    course = await middleware_dal.check_course(course_id=course_id)
    if not course:
        return JSONResponse(status_code=200, content={"message": "False"})
    return JSONResponse(status_code=200, content={"message": "True"})


@router.get('/core/middleware/check_course_exists_with_user/{course_id}', status_code=200)
async def check_course_with_user(
    course_id: int,
    user_id: str,
    middleware_dal: MiddlewareDAL = Depends(get_middleware_dal),
):
    course = await middleware_dal.check_course_with_user(course_id=course_id, user_id=user_id)
    if not course:
        return JSONResponse(status_code=200, content={"message": "False"})
    return JSONResponse(status_code=200, content={"message": "True"})


@router.get('/core/middleware/check_achievement_exists/{course_id}', status_code=200)
async def check_achievement(
    achievement_id: int, middleware_dal: MiddlewareDAL = Depends(get_middleware_dal)
):
    course = await middleware_dal.check_achievement(achievement_id)
    if not course:
        return JSONResponse(status_code=200, content={"message": "False"})
    return JSONResponse(status_code=200, content={"message": "True"})


@router.get('/core/middleware/check_lesson_exists/{lesson_id}', status_code=200)
async def check_lesson(
    lesson_id: int, middleware_dal: MiddlewareDAL = Depends(get_middleware_dal)
):
    lesson = await middleware_dal.check_lesson(lesson_id)
    if not lesson:
        return JSONResponse(status_code=200, content={"message": "False"})
    return JSONResponse(status_code=200, content={"message": "True"})


@router.get('/core/middleware/check_homework_exists/{homework_id}', status_code=200)
async def check_homework(
    homework_id: int, middleware_dal: MiddlewareDAL = Depends(get_middleware_dal)
):
    homework = await middleware_dal.check_homework(homework_id)
    if not homework:
        return JSONResponse(status_code=200, content={"message": "False"})
    return JSONResponse(status_code=200, content={"message": "True"})


@router.get('/core/middleware/get_users_follows/{user_id}')
async def get_user_follows(
    user_id, middleware_dal: MiddlewareDAL = Depends(get_middleware_dal)
):
    followings = await middleware_dal.get_user_with_following(user_id)
    return followings


@router.get('/core/middleware/get_users_followers/{user_id}')
async def get_user_followers(
    user_id, middleware_dal: MiddlewareDAL = Depends(get_middleware_dal)
):
    followers = await middleware_dal.get_user_with_followers(user_id)
    user = await middleware_dal.get_user(user_id)
    return [user, followers]


@router.post('/core/middleware/course/subscribe')
async def subscribe_to_course(
    request: schemas.Subscription,
    middleware_dal: MiddlewareDAL = Depends(get_middleware_dal),
):
    course = await middleware_dal.get_course(request.course_id)
    user = await middleware_dal.get_user_with_sub_course(request.user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Пользователя не существует",
        )
    if course in user.subscribed_courses:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Вы уже подписаны на курс",
        )
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Курса не найдено",
        )
    course_owner = await middleware_dal.get_user_by_course(course.user_id)
    if not course_owner:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Владельца курса не найдено",
        )
    if not course_owner.sold_courses:
        course_owner.sold_courses = 0
    course_owner.sold_courses += 1
    user.subscribed_courses.append(course)
    await send_subscription_notifications(user.id, course)
    await get_achievements(course.user_id, middleware_dal)
    return "Вы подписались на курс"


@router.post('/core/middleware/course/email-subscribe')
async def subscribe_to_course_by_email(
    request: schemas.EmailSubscription,
    middleware_dal: MiddlewareDAL = Depends(get_middleware_dal),
):
    course = await middleware_dal.get_course(request.course_id)
    user = await middleware_dal.get_user_with_sub_cours_by_email(request.email)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Пользователь не найден",
        )
    if str(user.id) != str(request.user_id):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content="Запрещено",
        )
    if course in user.subscribed_courses:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Вы уже подписаны на курс",
        )
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Курса не найдено",
        )
    course_owner = await middleware_dal.get_user_by_course(course.user_id)
    if not course_owner:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Владельца курса не найдено",
        )
    if not course_owner.sold_courses:
        course_owner.sold_courses = 0
    course_owner.sold_courses += 1
    user.subscribed_courses.append(course)
    await get_achievements(course.user_id, middleware_dal)
    return "Вы подписались на курс"


@router.post('/core/middleware/course/unsubscribe')
async def unsubscribe_to_course(
    request: schemas.Subscription,
    middleware_dal: MiddlewareDAL = Depends(get_middleware_dal),
):
    course = await middleware_dal.get_course(request.course_id)
    user = await middleware_dal.get_user_with_sub_course(request.user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Пользователь не найден",
        )
    if course not in user.subscribed_courses:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Вы не подписаны",
        )
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Курса не найдено",
        )
    user.subscribed_courses.remove(course)
    return "Курс удален из подписок"


@router.post('/core/middleware/course/email-unsubscribe')
async def unsubscribe_to_course_by_email(
    request: schemas.EmailSubscription,
    middleware_dal: MiddlewareDAL = Depends(get_middleware_dal),
):
    course = await middleware_dal.get_course(request.course_id)
    user = await middleware_dal.get_user_with_sub_cours_by_email(request.email)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Пользователь не найден",
        )
    if str(user.id) != str(request.user_id):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content="Запрещено",
        )
    if course not in user.subscribed_courses:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Вы не подписаны",
        )
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Курса не найдено",
        )
    user.subscribed_courses.remove(course)
    return "Курс удален из подписок"


@router.get('/core/middleware/user/add_achievements/{user_id}/{quantity}')
async def add_achievement(
    user_id,
    quantity,
    middleware_dal: MiddlewareDAL = Depends(get_middleware_dal),
):
    user = await middleware_dal.get_user_with_achievements(user_id)
    if quantity == '100000':
        title = '100000 комментариев'
        achievement = await middleware_dal.get_achievements_by_title(title)
        user.achievements.append(achievement)
    if quantity == '10000':
        title = '10000 комментариев'
        achievement = await middleware_dal.get_achievements_by_title(title)
        user.achievements.append(achievement)
    if quantity == '1000':
        title = '1000 комментариев'
        achievement = await middleware_dal.get_achievements_by_title(title)
        user.achievements.append(achievement)
    return 'ok'


@router.get('/core/middleware/get_course_obj/{course_id}', response_model=MyCourseOut)
async def get_course_obj(
    course_id: int, middleware_dal: MiddlewareDAL = Depends(get_middleware_dal)
):
    course = await middleware_dal.get_course(course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Курса не найдено",
        )
    return MyCourseOut.from_orm(course)


@router.get('/core/middleware/get_lesson_obj/{lesson_id}', response_model=LessonOut)
async def get_lesson_obj(
    lesson_id: int, middleware_dal: MiddlewareDAL = Depends(get_middleware_dal)
):
    lesson = await middleware_dal.get_lesson_with_course(lesson_id)
    if not lesson:
        return JSONResponse(
                       status_code=status.HTTP_400_BAD_REQUEST,
                       content="Урока не найдено"
        )
    return LessonOut.from_orm(lesson)


@router.get('/core/middleware/get_user_obj/{user_id}', response_model=UserOut)
async def get_user_obj(
    user_id: UUID4, middleware_dal: MiddlewareDAL = Depends(get_middleware_dal)
):
    user = await middleware_dal.get_user(user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Пользователя не найдено",
        )
    return UserOut.from_orm(user)


@router.get('/core/middleware/get_superuser_token')
async def unsubscribe_to_course(
    middleware_dal: MiddlewareDAL = Depends(get_middleware_dal),
):
    token = await middleware_dal.get_superuser_token()
    return token


@router.post('/core/middleware/upload/avatar', status_code=200)
async def upload_avatar(request: Avatar, file_dal: FileDAL = Depends(get_file_dal)):
    if request.course_id:
        await file_dal.upload_course_cover(request)
        message = "Course cover"
    elif request.achievement_id:
        await file_dal.upload_achievement_avatar(request)
        message = "Achievement cover"
    else:
        await file_dal.upload_avatar(request)
        message = "User profile avatar"
    return JSONResponse(content=f"Successfully added {message}")


@router.post('/core/middleware/upload/file', status_code=200)
async def upload_file(request: Content, file_dal: FileDAL = Depends(get_file_dal)):
    await file_dal.upload_content_file(request)
    message = "Content file added"
    return JSONResponse(content=f"Successfully added {message}")


# To get course if user is owner
@router.get('/core/middleware/get_content_info/{content_id}')
async def get_content_info(
    content_id: int, user_id: str, content_dal: ContentDAL = Depends(get_content_dal)
):
    content_info = await content_dal.get_content_information(
        content_id=content_id, user_id=user_id
    )
    return content_info
