from wtforms import Form, StringField, PasswordField, validators


class LoginForm(Form):
    email = StringField('Email', [validators.Length(min=4, max=30)])
    password = PasswordField('Password', [validators.Length(min=8, max=20)])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.password.widget.hide_value = False


class RegisterForm(LoginForm):
    confirm_password = PasswordField('Confirm', [validators.equal_to('Password', message='Passwords must match')])