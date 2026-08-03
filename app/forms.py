from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms import IntegerField, TextAreaField, BooleanField, ValidationError
from wtforms.validators import DataRequired, InputRequired, Optional, Length, NumberRange, Regexp


class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(message='Vui lòng nhập tên đăng nhập')])
    password = PasswordField('Mật khẩu', validators=[DataRequired(message='Vui lòng nhập mật khẩu')])
    submit = SubmitField('Đăng nhập')


class CartForm(FlaskForm):
    quantity = IntegerField('Số lượng', validators=[InputRequired(message='Vui lòng nhập số lượng'), NumberRange(min=1, message='Số lượng phải từ 1 trở lên')])


class ProductForm(FlaskForm):
    name = StringField('Tên sản phẩm', validators=[Optional(), Length(max=200)])
    price = IntegerField('Giá (VND)', validators=[InputRequired(message='Vui lòng nhập giá'), NumberRange(min=0, message='Giá không được âm')])
    cost_price = IntegerField('Giá nhập (VND)', validators=[Optional(), NumberRange(min=0, message='Giá nhập không được âm')])
    brand = StringField('Thương hiệu', validators=[Optional(), Length(max=100)])
    measurements = TextAreaField('Số đo', validators=[Optional()])
    description = TextAreaField('Mô tả', validators=[Optional()])
    quantity = IntegerField('Tồn kho', validators=[InputRequired(message='Vui lòng nhập tồn kho'), NumberRange(min=0, message='Tồn kho không được âm')], default=1)
    discontinued = BooleanField('Ngừng bán sản phẩm này')
    sku = StringField('Mã sản phẩm (SKU)', validators=[Optional(), Length(max=100)])
    sort_order = IntegerField('Thứ tự hiển thị', validators=[Optional()], default=0)
    admin_note = TextAreaField('Ghi chú nội bộ', validators=[Optional()])
    submit = SubmitField('Lưu sản phẩm')


class CheckoutForm(FlaskForm):
    customer_name = StringField('Họ và tên', validators=[DataRequired(message='Vui lòng nhập họ và tên.'), Length(max=100, message='Tên không được quá 100 ký tự.')])
    customer_phone = StringField('Số điện thoại', validators=[DataRequired(message='Vui lòng nhập số điện thoại.'), Regexp(r'^\+?[\d\s-]{8,15}$', message='Số điện thoại phải có 8–11 chữ số.')])
    customer_address = TextAreaField('Địa chỉ', validators=[DataRequired(message='Vui lòng nhập địa chỉ.'), Length(max=500, message='Địa chỉ không được quá 500 ký tự.')])
    customer_note = TextAreaField('Ghi chú', validators=[Optional(), Length(max=1000, message='Ghi chú không được quá 1000 ký tự.')])
    website = StringField()  # honeypot: bot điền -> silent reject ở route, không validator
    submit = SubmitField('Đặt hàng')

    def validate_customer_phone(self, field):
        # Regexp chỉ kiểm tra charset + độ dài thô; đếm chữ số là check chính (8–11 chữ số).
        digits = ''.join(ch for ch in field.data if ch.isdigit())
        if not (8 <= len(digits) <= 11):
            raise ValidationError('Số điện thoại phải có 8–11 chữ số.')
