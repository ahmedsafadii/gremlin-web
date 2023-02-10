from django.utils.translation import gettext_lazy as _


class FieldsEntity:
    fields = {
        "star": _("star"),
        "comment": _("comment"),
        "status": _("status"),
        "booking": _("booking"),
        "deviceId": _("device id"),
        "platform": _("platform"),
        "version": _("version"),
        "paymentMethod": _("payment method"),
        "garden": _("garden"),
        "spot": _("spot"),
        "packagePrice": _("package price"),
        "coupon": _("coupon"),
        "package": _("package"),
        "description": _("description"),
        "auth": _("auth"),
        "documents": _("documents"),
        "images": _("images"),
        "logo": _("logo"),
        "firstName": _("first name"),
        "lastName": _("last name"),
        "identity": _("identity"),
        "truckName": _("truck name"),
        "category": _("category"),
        "email": _("email address"),
        "password": _("password"),
        "country": _("country"),
        "mobileNumber": _("mobile number"),
        "code": _("code"),
        "password1": _("password"),
        "password2": _("confirm password"),
        "non_field_errors": _("non_field_errors"),
        "confirmNewPassword": _("Confirm new password"),
        "newPassword": _("New password"),
        "oldPassword": _("Old password"),
        "request_change_password": _("Request change password"),
        "isRenew": _("Is renew"),
        "error": _("Error"),
        "general": _("general"),
        "accessToken": _("Access token"),
        "question": _("Question"),
        "receipt": _("Receipt"),
    }

    codes = {
        "required": _("is required."),
        "blank": _("can not be blank."),
        "invalid": _("invalid"),
        "auth": _("Auth"),
        "min_length": _("Min length"),
        "not_a_list": _("No list found"),
        "null": _("is required."),
    }


def get_field(key, error):
    print(key, error)
    if key in FieldsEntity.fields:
        if not hasattr(error[0], "code"):
            return error
        else:
            code = error[0].code
        if code in [
            "invalid",
            "non_field_errors",
            "auth",
            "not_a_list",
            "min_length",
            "general",
        ]:
            return error[0].title()
        else:
            return (
                "Field"
                + " "
                + FieldsEntity.fields[key]
                + " "
                + FieldsEntity.codes[code]
            )
    else:
        return _("Unknown field error") + " - " + key
