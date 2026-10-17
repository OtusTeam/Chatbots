from aiogram import Router, types, F


router = Router()


@router.message(F.photo)
async def photo_handler(message: types.Message):
    user_id = message.from_user.id
    photo = message.photo
    print(photo)
    print(user_id)


@router.message(F.video)
async def photo_handler(message: types.Message):
    user_id = message.from_user.id
    photo = message.video
    print(photo)
    print(user_id)