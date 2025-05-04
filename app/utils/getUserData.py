from app.utils import getPublicData
from app.models import User

def getUserData(id):

    user = User.objects.filter(id=id).first()

    return user