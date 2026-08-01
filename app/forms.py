from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms import IntegerField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, InputRequired, Optional, Length, NumberRange


class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(message='Vui lòng nhập tên đăng nhập')])
    password = PasswordField('Mật khẩu', validators=[DataRequired(message='Vui lòng nhập mật khẩu')])
    submit = SubmitField('Đăng nhập')


class ProductForm(FlaskForm):
    name = StringField('Tên sản phẩm', validators=[DataRequired(message='Vui lòng nhập tên sản phẩm'), Length(max=200)])
    price = IntegerField('Giá (VND)', validators=[InputRequired(message='Vui lòng nhập giá'), NumberRange(min=0, message='Giá không được âm')])
    brand = StringField('Thương hiệu', validators=[Optional(), Length(max=100)])
    measurements = TextAreaField('Số đo', validators=[Optional()])
    description = TextAreaField('Mô tả', validators=[Optional()])
    quantity = IntegerField('Tồn kho', validators=[InputRequired(message='Vui lòng nhập tồn kho'), NumberRange(min=0, message='Tồn kho không được âm')], default=0)
    discontinued = BooleanField('Ngừng bán sản phẩm này')
    sku = StringField('Mã sản phẩm (SKU)', validators=[Optional(), Length(max=100)])
    sort_order = IntegerField('Thứ tự hiển thị', validators=[Optional()], default=0)
    admin_note = TextAreaField('Ghi chú nội bộ', validators=[Optional()])
    submit = SubmitField('Lưu sản phẩm')
