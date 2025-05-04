from app.models import User

def modifyUserData(username,formData,file):

    user = User.objects.get(username=username)
    user.username = formData['username']
    user.textarea = formData['shortinfo']
    if file.get('avatar') != None:
        user.avatar = file.get('avatar')

    user.save()
    # id = user.id
    # User.objects.filter(id=id).update(username=user.username, textarea=user.textarea, avatar=user.avatar)

