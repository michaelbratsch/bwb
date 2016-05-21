from register.models import Bicycle, Candidate
import django_tables2 as tables


class CandidateTable(tables.Table):
    first_name = tables.Column(verbose_name='First Name')
    last_name = tables.Column(verbose_name='Last Name')
    date_of_birth = tables.Column(verbose_name='Date of Birth')
    date_of_registration = tables.Column(
        verbose_name='Date of Registration',
        accessor='user_registration.time_of_registration')
    current_status = tables.Column(
        verbose_name='Status',
        accessor='get_status')
    bicycle = tables.Column(
        verbose_name='Bicycle',
        accessor='bicycle',
        order_by='bicycle.bicycle_number')

    class Meta:
        model = Candidate
        attrs = {'class': 'bootstrap', 'width': '1000%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no canditates in the database."
        sequence = ('current_status', '...')


class BicycleTable(tables.Table):

    class Meta:
        model = Bicycle
        attrs = {'class': 'bootstrap', 'width': '100%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no bicycles in the database."
