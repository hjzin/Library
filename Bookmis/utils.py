#权限检查
def permission_check(user):
    if user.is_authenticated():
        return user.user.permission > 1
    else:
        return False