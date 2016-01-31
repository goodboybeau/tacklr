from mongoengine import Document, StringField, IntField, EmailField, BooleanField, connect


class User(Document):
    email = EmailField(max_length=50, unique=True, required=True)
    hashed_password = StringField(max_length=50, required=True)
    authenticated = BooleanField(default=False)
    active = BooleanField(default=False)
    anonymous = BooleanField(default=False)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return self.anonymous

    def get_id(self):
        print 'getting id', u''.join(str(self.email))
        return u''.join(str(self.email))

    def try_login(self, hpw):
        if self.hashed_password == hpw:
            self.authenticated = True
            self.active = True
            self.save()
            return True
        return False


if __name__ == '__main__':
    connect('test')

    u = User.objects.get(email='test@email.com')

    if u:
        print u.email

    u.hashed_password = 'abcdefgh'
    print u.save()

