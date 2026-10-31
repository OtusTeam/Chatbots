from aiogram import Router, types, F

from app.front.bot_entrypoint import logger


router = Router()


@router.message(F.photo)
async def photo_handler(message: types.Message):
    user_id = message.from_user.id
    photo_list = message.photo or []

    if not photo_list:
        logger.warning("Фото: сообщение пришло, но photo_list=None")

    photo = photo_list[-1]

    logger.info(f"Фото получено. Размер {photo.file_size} байт")
    # print(photo)
    # print(user_id)

    await message.answer("Фото получено")


@router.message(F.video)
async def video_handler(message: types.Message):
    user_id = message.from_user.id
    video = message.video

    if video is None:
        logger.warning("Видео: сообщение пришло, но video=None")

    logger.info(f"Видео получено. Размер {video.file_size} байт")

    await message.answer("Видео получено")
    # print(video)
    # print(user_id)