from db.models import *
from db.functions import *

from sqlalchemy.exc import IntegrityError, NoResultFound


def ensure_admin_exists():
    ID = 1
    USERNAME = 'a.dminovich'
    PASSWORD = 'FDSAr342fsd#$32fsc!@#$f'
    LEVEL = 2
    KPI = 999
    try:
        admin_user = get_user_by_id(ID)
    except NoResultFound:
        admin_user, session = create_user(
            user_id=ID,
            username=USERNAME,
            password=PASSWORD,
            level=LEVEL,
            kpi=KPI,
        )
    return admin_user


def ensure_admin_chat(non_admin_user_id: int) -> Chat:
    ADMIN_ID = 1
    admin = get_user_by_id(ADMIN_ID)
    non_admin = get_user_by_id(non_admin_user_id)
    if (chat := find_chat(admin.id, non_admin.id)) is None:
        chat = create_chat(admin.id, non_admin.id)
    return chat


if __name__ == '__main__':
    admin = ensure_admin_exists()
    user, user_session = create_random_support_user()
    admin_chat = ensure_admin_chat(user.id)
    create_message(admin_chat.id, admin.id, "Work hard, its your duty >:(")
