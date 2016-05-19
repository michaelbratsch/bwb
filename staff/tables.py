import django_tables2 as tables

from register.models import Bicycle, Candidate


class CandidateTable(tables.Table):
    first_name = tables.Column(verbose_name='First Name')
    last_name = tables.Column(verbose_name='Last Name')
    date_of_birth = tables.Column(verbose_name='Date of Birth')

    class Meta:
        model = Candidate
        attrs = {'class': 'bootstrap', 'width': '100%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no canditates in the database."


class BicycleTable(tables.Table):
    class Meta:
        model = Bicycle
        attrs = {'class': 'bootstrap', 'width': '100%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no bicycles in the database."
