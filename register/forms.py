from datetime import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML, Div
from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import SelectDateWidget, TextInput
from django.utils.translation import ugettext as _, ugettext_lazy
from phonenumber_field.formfields import PhoneNumberField
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

from register.models import UserRegistration, Candidate, SiteConfiguration


# ToDo: Only take people into account that do not have a bicycle.
def open_for_registration():
    return Candidate.total_in_line() < SiteConfiguration.get_solo(
    ).max_number_of_registrations


TOO_MANY_REGISTRATIONS_ERROR = _(
    'Due to too many registrations, it is currently not possible to register '
    'for a bicycle.')

BAD_FORMAT_NUMBER = _('This is not a properly formatted phone number.')
INVALID_NUMBER = _('This is not a valid phone number.')
INVALID_MOBILE_NUMBER = _('This is not a valid mobile phone number.')

TERMS_AND_CONDITIONS_ERROR = _(
    'You need to agree with the terms and conditions.')
MULTIPLE_REGISTRATION_ERROR = _(
    'A user with this name and date of birth is already registered. '
    'It is not allowed to register multiple times!')
EMAIL_OR_PHONE_ERROR = _('Please fill out email or mobile phone number.')


# ToDo: get these prefixes from somewhere else, otherwise they will
# eventually become outdated
MOBILE_PHONE_PREFIXES = ['01511',  # Deutsche Telekom
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


def parse_mobile_number(value):
    def is_mobile_number(parsed_number):
        for prefix in MOBILE_PHONE_PREFIXES:
            if str(parsed_number.national_number).startswith(prefix[1:]):
                return True
        return False

    try:
        parsed_number = phonenumbers.parse(value, 'DE')
    except NumberParseException:
        raise ValidationError(BAD_FORMAT_NUMBER)

    if not phonenumbers.is_valid_number_for_region(parsed_number, 'de'):
        raise ValidationError(INVALID_NUMBER)

    if not is_mobile_number(parsed_number):
        raise ValidationError(INVALID_MOBILE_NUMBER)

    return phonenumbers.format_number(
        parsed_number,
        phonenumbers.PhoneNumberFormat.INTERNATIONAL)


class MyPhoneNumberField(PhoneNumberField):

    def to_python(self, value):
        if value:
            value = parse_mobile_number(value)

        return super(MyPhoneNumberField, self).to_python(value)


class SelectDateOfBirthWidget(SelectDateWidget):

    def __init__(self, *args, **kwargs):
        current_year = datetime.now().year
        super(SelectDateOfBirthWidget, self).__init__(
            years=range(1900, current_year)[::-1], *args, **kwargs)


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=False, label=ugettext_lazy('Email'),
                             widget=TextInput)
    mobile_number = MyPhoneNumberField(
        required=False,
        label=ugettext_lazy('Mobile phone number'))
    bicycle_kind = forms.ChoiceField(
        choices=UserRegistration.BICYCLE_CHOICES,
        required=True,
        label=ugettext_lazy('Bicycle kind'))
    agree = forms.BooleanField(
        required=False,
        label=ugettext_lazy("Agree with Terms and Conditions"))

    class Meta:
        model = Candidate
        fields = ('first_name', 'last_name', 'date_of_birth',
                  'email', 'mobile_number', 'bicycle_kind', 'agree')
        labels = {'first_name': ugettext_lazy('First name'),
                  'last_name': ugettext_lazy('Last name'),
                  'date_of_birth': ugettext_lazy('Date of birth')}
        widgets = {'date_of_birth': SelectDateOfBirthWidget}

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        lines_of_body = [
            _('You can only buy one bike per person.'),
            _('Please do not register twice.'),
            _('If you want a bike for your children, please also register '
              'them.'),
            _('We do not sell new bikes.'),
            _('All bikes are donated and used.'),
            _('We only sell road-worthy bikes.'),
            _('You can resell your bike to us, if you do not need it '
              'anymore.'),
            _('Our bikes always need repair work. Please bring some time and '
              'help us to repair your bike.')]

        content_dict = {
            'heading': _("Terms of use"),
            'subheading': _("Our terms of use are the following:"),
            'body': " ".join('<li>%s</li>' % line for line in lines_of_body)}

        def wrap_field(*args):
            return Div(*args, css_class='col-md-6 col-xs-12')

        self.helper.layout = Layout(
            wrap_field(Field('first_name'),
                       Field('last_name'),
                       Field('date_of_birth')),
            wrap_field(Field('email'),
                       Field('mobile_number'),
                       Field('bicycle_kind')),
            Div(
                HTML(
                    """ <label for="id_terms_of_use" class="control-label">
                            %(heading)s
                        </label>
                        <div class="controls" id="id_terms_of_use">
                            <div style="border: 1px solid #e5e4e4;
                            overflow: auto;">
                                <p>%(subheading)s</p>
                                <ul>
                                    %(body)s
                                </ul>
                            </div>
                        </div>""" % content_dict),
                Field('agree'), css_class='col-xs-12')
        )

        self.helper.add_input(Submit('submit', _('Submit'),
                                     css_class='col-xs-3 btn-info'))

    def clean_mobile_number(self):
        mobile_number_uncleaned = self.data.get('mobile_number')

        if mobile_number_uncleaned:
            return parse_mobile_number(mobile_number_uncleaned)

        return None

    def clean_agree(self):
        agree = bool(self.data.get('agree'))
        if not agree:
            raise ValidationError(TERMS_AND_CONDITIONS_ERROR)
        return agree

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        if not open_for_registration():
            raise ValidationError(TOO_MANY_REGISTRATIONS_ERROR)

        email = cleaned_data.get('email')
        mobile_number = cleaned_data.get('mobile_number')

        # Email or phone number needs to be present
        if not (email or mobile_number):
            raise ValidationError(EMAIL_OR_PHONE_ERROR)

        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        date_of_birth = cleaned_data.get('date_of_birth')

        if Candidate.get_matching(first_name=first_name,
                                  last_name=last_name,
                                  date_of_birth=date_of_birth):
            raise ValidationError(MULTIPLE_REGISTRATION_ERROR)

        return cleaned_data
