from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML
from django import forms
from django.utils.translation import ugettext
from phonenumber_field.formfields import PhoneNumberField
from phonenumbers.phonenumberutil import NumberParseException
import phonenumbers

from django.core.exceptions import ValidationError

from register.models import max_name_length, User_Registration, Candidate


# ToDo: get these prefixes from somewhere else, otherwise they will
# eventually become outdated
mobile_phone_prefixes = ['01511',  # Deutsche Telekom
                         '01512',
                         '01514',
                         '01515',
                         '01516',
                         '01517',
                         '0160',
                         '0170',
                         '0171',
                         '0175',
                         '01520',  # Vodafone
                         '01521',
                         '01522',
                         '01523',
                         '01525',
                         '01526',
                         '01529',
                         '0162',
                         '0172',
                         '0173',
                         '0174',
                         '01570',  # E-Plus
                         '01573',
                         '01575',
                         '01577',
                         '01578',
                         '01579',
                         '0163',
                         '0177',
                         '0178',
                         '01590',  # O2
                         '0176',
                         '0179']


bad_format_number = ugettext('This is not a properly formatted phone number.')
invalid_number = ugettext('This is not a valid phone number for this region.')
invalid_mobile_number = ugettext('This is not a valid mobile phone number.')


def parse_phone_number(value):
    def is_mobile_number(parsed_number):
        for prefix in mobile_phone_prefixes:
            if str(parsed_number.national_number).startswith(prefix[1:]):
                return True
        return False

    try:
        parsed_number = phonenumbers.parse(value, 'DE')
    except NumberParseException:
        raise ValidationError(bad_format_number)

    if not phonenumbers.is_valid_number_for_region(parsed_number, 'de'):
        raise ValidationError(invalid_number)

    if not is_mobile_number(parsed_number):
        raise ValidationError(invalid_mobile_number)

    return phonenumbers.format_number(parsed_number,
                                      phonenumbers.PhoneNumberFormat.E164)


class MyPhoneNumberField(PhoneNumberField):

    def to_python(self, value):
        if value:
            value = parse_phone_number(value)

        return super(MyPhoneNumberField, self).to_python(value)


terms_and_conditions_error = ugettext(
    'You need to agree with the terms and conditions.')
multiple_registration_error = ugettext(
    'A user with this name and date of birth is already registered. '
    'It is not allowed to register multiple times!')
email_or_phone_error = ugettext('Please fill out email or phone number.')


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=max_name_length, required=True)
    last_name = forms.CharField(max_length=max_name_length, required=True)
    date_of_birth = forms.DateField(required=True)

    email = forms.EmailField(required=False)
    phone_number = MyPhoneNumberField(required=False)
    bicycle_kind = forms.ChoiceField(
        choices=User_Registration.BICYCLE_CHOICES,
        required=True)
    agree = forms.BooleanField(required=False,
                               label="Agree with Terms and Conditions")

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field('first_name'),
            Field('last_name'),
            Field('date_of_birth', id='datepicker'),
            Field('email'),
            Field('phone_number'),
            Field('bicycle_kind'),
            HTML(
                """ <label for="id_terms_of_use" class="control-label">
                        {%load i18n %}{% trans "Terms of use" %}
                    </label>
                    <div class="controls" id="id_terms_of_use">
                        <div style="border: 1px solid #e5e4e4;
                        overflow: auto; padding: 10px;">
                            {% blocktrans %}
                            <p>Our terms of use are the following:</p>
                            <li>You can only buy one bike per person.</li>
                            <li>Please do not register twice.</li>
                            <li>If you want a bike for your children, please
                            also register them.</li>
                            <li>We do not sell new bikes.</li>
                            <li>All bikes are donated and used.</li>
                            <li>We only sell roadworthy bikes.</li>
                            <li>You can resell your bike to us, if you do not
                            need it anymore.</li>
                            <li>Our bikes alway need repair work. Please bring
                            some time and help us repairing your bike.</li>
                            {% endblocktrans %}
                        </div>
                    </div>"""),
            Field('agree'))

        self.helper.add_input(Submit('submit', 'Submit',
                                     css_class='col-xs-3 btn-info'))

    def clean_phone_number(self):
        phone_number_uncleaned = self.data.get('phone_number')

        if phone_number_uncleaned:
            return parse_phone_number(phone_number_uncleaned)

        return None

    def clean_agree(self):
        agree = bool(self.data.get('agree'))
        if not agree:
            raise ValidationError(terms_and_conditions_error)
        return agree

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        email = cleaned_data.get('email')
        phone_number = cleaned_data.get('phone_number')

        # Email or phone number needs to be present
        if not (email or phone_number):
            raise ValidationError(email_or_phone_error)

        try:
            first_name = cleaned_data['first_name']
            last_name = cleaned_data['last_name']
            date_of_birth = cleaned_data['date_of_birth']
        except KeyError:
            # If not caught, this key error prevents from testing the
            # form validation errors for first_name, last_name and
            # date_of_birth.
            pass
        else:
            if Candidate.get_matching(first_name=first_name,
                                      last_name=last_name,
                                      date_of_birth=date_of_birth):
                raise ValidationError(multiple_registration_error)

        return cleaned_data
