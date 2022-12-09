# coding:utf8
from __future__ import unicode_literals
from .. import Member, BookingKind, User, Allotment
from ..log import user_data_log, log_with_user
from ..base import parse_date
from sepaxml import SepaDD, SepaTransfer
from io import StringIO, BytesIO
from pyramid.decorator import reify
from pyramid.response import FileIter
import csv
import datetime
import decimal
import json
import pyramid.interfaces
import risclog.sqlalchemy.interfaces
import sqlalchemy
import sqlalchemy.sql.expression
import sw.allotmentclub
import sw.allotmentclub.base
import sw.allotmentclub.version
import transaction
import xlsxwriter
import openpyxl
import zope.component
import zope.interface


UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
CONTENTTYPEENDING = {
    'image/jpg': 'JPG',
    'image/jpeg': 'JPG',
    'image/pjpeg': 'JPG',
    'image/gif': 'GIF',
    'image/tif': 'TIF',
    'image/png': 'PNG',
    'application/pdf': 'PDF',
    'application/x-unknown-application-pdf': 'PDF',
    'application/msword': 'Word',
    'application/vnd.ms-excel': 'Excel',
    'application/vnd.ms-powerpoint': 'Powerpoint',
    'application/x-zip-compressed': 'ZIP',
    'application/zip': 'ZIP',
    'audio/mpeg': 'MP3',
    'audio/mp3': 'MP3',
    'audio/mpg': 'MP3',
    'video/mpeg': 'MPEG',
    'video/x-ms-wmv': 'WMV',
    'video/mpg': 'MPG',
    'default': ''}


def route_url(route_name, request):
    """Returns the configured url for a route."""
    mapper = request.registry.getUtility(pyramid.interfaces.IRoutesMapper)
    path = mapper.get_route(route_name).path
    if route_name == 'booking_list':
        # Short route: we currently have only 1 backing account
        path = path.replace('{id}', '1')
    return path


def get_view_for_route(route_name, request):
    request_iface = request.registry.queryUtility(
        pyramid.interfaces.IRouteRequest,
        name=route_name,
        default=pyramid.interfaces.IRequest)
    view = request.registry.adapters.lookup(
        (pyramid.interfaces.IViewClassifier, request_iface,
         zope.interface.providedBy(request.context)),
        pyramid.interfaces.ISecuredView, default=None)
    if view is None:
        raise TypeError('The requested route `{}` is not configured.'.format(
            route_name))
    return view


def route_permitted(route_name, request):
    """Check whether the user is allowed to use a route.

    Code inspired by pyramid.security.view_execution_permitted
    """
    current_route = request.matched_route.name
    request.matched_route.name = route_name
    view = get_view_for_route(route_name, request)
    result = view.__permitted__(request.context, request)
    request.matched_route.name = current_route
    return result


def format_size(value, request):
    if not value:
        return
    value = float(value)
    unit = 0
    while value > 1024:
        value = value / 1024.0
        unit += 1
    return '%.2f %s' % (value, UNITS[unit])


def format_mimetype(value, request):
    return CONTENTTYPEENDING.get(value, value)


def to_string(col, parentheses=False):
    col_string = sqlalchemy.func.cast(col, sqlalchemy.String)
    if parentheses:
        return to_string('(').concat(col_string).concat(')')
    else:
        return col_string


def string_agg(col, delimiter='/'):
    return sqlalchemy.func.string_agg(
        to_string(col), to_string(delimiter),
        order_by=col.asc())


def date(value, request=None):
    if value is None:
        return ''
    return value.strftime('%d.%m.%Y')


def iso_to_german_date(value, request=None):
    if value is None:
        return ''
    if isinstance(value, datetime.date):
        return date(value)
    try:
        return date(parse_date(value))
    except ValueError:
        return value


def date_time(value, request=None):
    if value is None:
        return ''
    return value.strftime('%d.%m.%Y %H:%M')


def datetime_now():
    return datetime.datetime.now()


def value_to_int(value):
    return int(float(value.replace('.', '').replace(',', '.')) * 10000)


def format_date(value, request=None):
    return value.strftime('%d.%m.%Y')


def format_eur(value, request=None, full=False):
    return sw.allotmentclub.base.format_eur(value, full)


def format_eur_with_color(value, request=None, full=False):
    if value is None:
        value = 0
    formatted = format_eur(value, request, full)
    if value > 0:
        formatted = '<span class="txt-color-green">%s</span>' % formatted
    if value < 0:
        formatted = '<span class="txt-color-red">%s</span>' % formatted
    return formatted


def format_kwh(x, request=None):
    return sw.allotmentclub.base.format_kwh(x)


def moneyfmt(value, places=2, curr='', sep=',', dp='.', pos='', neg='-',
             trailneg='', request=None):
    """Convert Decimal to a money formatted string.

    see: http://docs.python.org/2/library/decimal.html#recipes
    Adapted to display currency symbol after the numbers.

    places:  required number of places after the decimal point
    curr:    optional currency symbol after the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> from decimal import Decimal
    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr=' EUR')
    u'-1,234,567.89 EUR'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    u'1.234.568-'
    >>> moneyfmt(d, curr=' EUR', neg='(', trailneg=')')
    u'(1,234,567.89 EUR)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    u'123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    u'<0.02>'
    >>> moneyfmt(Decimal('12.305'))
    u'12.31'
    >>> moneyfmt(Decimal('-12.305'))
    u'-12.31'

    """
    q = decimal.Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    build(curr)
    for i in range(places):
        build(next() if digits else '0')
    if places:
        build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(neg if sign else pos)
    return ''.join(reversed(result))


def percent(*args, **kw):
    """Formatter for percent values."""
    return number(*args, formatting_options={'curr': ' %'}, **kw)


def get_selected_year():
    request = pyramid.threadlocal.get_current_request()
    default = datetime.datetime.now().year
    if not request:
        return default
    return int(request.GET.get('for_year', default))


def number(*args, **kw):
    """Formatter for ordinary numbers."""
    unit = kw.pop('unit', 1)
    formatting_options = dict(dp=',', sep='.')
    formatting_options.update(kw.pop('formatting_options', {}))

    def formatter(value, request=None):
        if value is None:
            return ''
        value /= unit
        if not isinstance(value, decimal.Decimal):
            value = decimal.Decimal(str(value))
        return moneyfmt(value, **formatting_options)

    kw.pop('request', None)
    if len(args) == 1 and not kw:
        # money is being used without arguments in table declaration. Default
        # and easy way
        return formatter(args[0])
    # Formatter is special cased:
    assert not args
    formatting_options.update(kw)
    return formatter


def boolean(value, request=None):
    return '✓' if value else ''


class View(object):

    result = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.result = {}
        self.update()
        if isinstance(self.result, dict):
            self.result['version'] = sw.allotmentclub.version.__version__
        return self.result

    def update(self):
        pass

    def form_submit(self):
        return (
            self.request.params and
            list(self.request.params.keys()) != ['for_year'])

    @property
    def active_members(self):
        return (
            Member.query()
            .join(Allotment, Allotment.member_id == Member.id)
        )


class AddEditBase(View):

    def get_form_attributes(self):
        form_attributes = []
        for item in self.form_attributes:
            form_attributes.append(item.copy())
        for item in form_attributes:
            funcname = 'autocomplete_{}'.format(item['name'])
            if hasattr(self, funcname):
                item['autocomplete'] = getattr(self, funcname)()
            if 'values' in item:
                values = []
                for value in item['values']:
                    value = value.copy()
                    if getattr(
                            self.context, item['name'], None) == value['id']:
                        value['selected'] = 'selected'
                    values.append(value)
                item['values'] = values
        return form_attributes

    def update_params(self, params):
        return


class AddView(AddEditBase):

    model = NotImplementedError
    context_id = None
    created = None

    def update(self):
        if self.form_submit():
            params = {}
            params.update(self.request.params)
            if self.context_id:
                params.update({self.context_id: self.context.id})
            self.update_params(params)
            self.created = self.model.create(**params)
            result = {'status': 'success'}
        else:
            form_attributes = self.get_form_attributes()
            result = {'status': 'success'}
            result.update({'data': {
                'form': form_attributes,
                'form_data': getattr(self, 'form_data', {}),
                'load_options': getattr(self, 'load_options', {}),
                'title': self.title}})
        self.result = result


class EditView(AddEditBase):

    def update(self):
        if self.form_submit():
            params = {}
            params.update(self.request.params)
            self.update_params(params)
            for key, value in params.items():
                if not value:
                    value = None
                setattr(self.context, key, value)
            result = {'status': 'success'}
        else:
            form_attributes = self.get_form_attributes()
            for item in form_attributes:
                item['value'] = getattr(self.context, item['name'], None)
            result = {'status': 'success'}
            result.update({'data': {
                'form': form_attributes,
                'title': self.title}})
        self.result = result


class EditJSFormView(AddEditBase):

    @property
    def members(self):
        return (
            Member.query()
            .filter(
                Member.organization_id == self.request.user.organization_id)
            .filter(Member.leaving_year.is_(None)))

    @property
    def member_source(self):
        return [
            {
                'token': member.id,
                'title': '{}, {} ({})'.format(
                    member.lastname,
                    member.firstname,
                    '/'.join(str(a.number)
                             for a in member.allotments) or 'n/a')
            }
            for member in self.members.order_by(Member.lastname).all()]

    @property
    def allotments(self):
        return (
            Allotment.query()
            .join(Member, Allotment.member_id == Member.id)
            .filter(
                Member.organization_id == self.request.user.organization_id)
        )

    @property
    def allotment_source(self):
        return [
            {
                'token': allotment.id,
                'title': '{} ({}, {})'.format(
                    str(allotment.number),
                    allotment.member.lastname,
                    allotment.member.firstname
                )
            }
            for allotment in self.allotments.order_by(Allotment.number)]

    @property
    def users(self):
        return (
            User.query()
            .filter(User.id != 42)
            .filter(User.organization_id == self.request.user.organization_id)
            .filter(sqlalchemy.or_(
                User.is_locked.is_(None), User.is_locked == '')))

    @property
    def user_source(self):
        return [
            {
                'token': user.id,
                'title': '{}, {} ({})'.format(
                    user.nachname,
                    user.vorname,
                    user.username)
            }
            for user in self.users.order_by(User.nachname).all()]

    @property
    def booking_kind_source(self):
        return [{'token': k.id, 'title': k.title}
                for k in BookingKind.query().all()]

    @property
    def accounting_year_source(self):
        result = []
        year = 2014
        now = datetime.datetime.now()
        current = now.year
        if now.month >= 8:
            current += 1
        while year <= current:
            result.append({'token': year, 'title': year})
            year += 1
        return result

    def resource_data_item_title(self, item):
        return item.filename

    def resource_data_item(self, item, route_name):
        return {
            'status': 'success',
            'resource': self.get_route(item, route_name),
            'id': item.id,
            'data': {'title': self.resource_data_item_title(item)}}

    @property
    def route_name(self):
        return self.request.matched_route.name

    def get_route(self, item, route):
        return '/api/' + route_url(
            route, self.request).replace('{id}', str(item.id))

    def get_result(self):
        save_url = self.get_route(self.context, self.route_name)
        result = {'status': 'success'}
        result.update({'data': {
            'load_options': self.load_options,
            'load_data': self.load_data,
            'url': save_url,
            'title': self.title}})
        return result

    def save(self, key, value):
        try:
            type_ = self.context.__table__.columns[key].type
        except Exception:
            type_ = None
        if (
            isinstance(type_, sqlalchemy.DateTime) or
            isinstance(type_, sqlalchemy.Date)
        ):
            value = parse_date(value)
        try:
            setattr(self.context, key, value)
        except sw.allotmentclub.model.ValidationError as e:
            return str(e)

    def update(self):
        try:
            json = self.request.json
        except ValueError:
            json = None
        file_ = self.request.params.get('file')
        if self.form_submit() and file_ is None:
            self.result = {
                'status': 'error',
                'msg': 'Ein unerwarteter Fehler ist aufgetreten'
            }
        elif file_ is not None:
            created, route_name = self.handle_upload(file_)
            transaction.savepoint()
            result = self.resource_data_item(created, route_name)
            log_with_user(user_data_log.info, self.request.user,
                          'Datei in %s %s hochgeladen.',
                          self.title.split(' ')[0], self.context.id)
        elif json and list(json.keys())[0] != 'attachments':
            error = self.save(
                list(json.keys())[0],
                list(json.values())[0])
            if error:
                result = {'status': 'error', 'msg': error}
            else:
                log_with_user(
                    user_data_log.info, self.request.user, '%s %s bearbeitet.',
                    self.title.split(' ')[0], self.context.id)
                result = {'status': 'success'}
        else:
            if not self.context.id:
                transaction.savepoint()
            result = self.get_result()
        self.result = result

    def handle_upload(self, file_):
        raise NotImplementedError('Handle in subclass.')


class DeleteView(View):

    model = NotImplementedError
    deleted = None
    mark_deleted = False

    def update(self):
        if self.mark_deleted:
            self.context.deleted = True
        else:
            db = zope.component.getUtility(
                risclog.sqlalchemy.interfaces.IDatabase
            )
            db.session.delete(self.context)
        self.deleted = True
        self.result = {'status': 'success'}
        self.log()

    def log(self):
        if self.deleted is not None:
            log_with_user(
                user_data_log.info, self.request.user,
                '%s %s gelöscht.', self.model.__name__,
                self.context.id)


class Query(object):

    _default_css_classes = {
        '#': 'hide',
        'Zählerstand': 'right',
        'Verbrauch': 'right',

    }

    filters = {}
    formatters = {}
    css_classes = {}
    data_hide = {}
    data_class = {}
    order_by = {}  # map column name to custom SQL ORDER BY expression
    disable_global_organization_filter = False

    def __init__(self, db, user, context=None):
        self.db = db
        self.user = user
        self.context = context

    def __call__(self):
        query = self.select()
        if not self.disable_global_organization_filter:
            query = query.filter(
                getattr(query._select_from_entity.columns,
                        'organization_id') ==
                self.user.organization_id)
        self._assert_columns(query, self.filters.keys(), 'filters')
        self._assert_columns(query, self.formatters.keys(), 'formatters')
        self._assert_columns(query, self.css_classes.keys(), 'css_classes')
        self._assert_columns(query, self.data_hide.keys(), 'data_hide')
        self._assert_columns(query, self.data_class.keys(), 'data_class')
        return query

    def _assert_columns(self, query, columns, kind):
        dialect = query.session.get_bind().dialect
        query_string = str(query.statement.compile(dialect=dialect))
        for col in columns:
            assert col in query_string, \
                "Column %r is in self.%s but not in query." % (col, kind)

    def select(self):
        raise NotImplementedError()


class QueryClient(object):

    query_class = NotImplemented

    @reify
    def query(self):
        db = zope.component.queryUtility(
            risclog.sqlalchemy.interfaces.IDatabase)
        return self.query_class(db, self.request.user, self.context)


class TableView(QueryClient):

    # default sort order: unordered, may be set in subclass
    default_order_by = None
    default_sort_direction = 'asc'  # allowed values: 'asc', 'desc'
    default_limit = None
    year_selection = False
    start_year = 2014
    available_actions = []

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def table_columns(self):
        css_classes = self.query._default_css_classes.copy()
        css_classes.update(self.query.css_classes)
        return [
            {'name': desc['name'],
             'css_class': css_classes.get(desc['name'], ''),
             'data-class': self.query.data_class.get(desc['name'], ''),
             'data-hide': self.query.data_hide.get(desc['name'], '')}
            for desc in self.query().column_descriptions]

    @property
    def order_by(self):
        """Order by default set on the class."""
        column = self.default_order_by
        direction = self.default_sort_direction
        if column:
            order_by = f"{column} {direction}"
        else:
            # No order required
            order_by = None
        return order_by

    @property
    def limit(self):
        return self.default_limit

    def data(self):
        query = self.query()
        order_by = self.order_by
        if order_by:
            query = query.order_by(sqlalchemy.text(order_by))
        limit = self.limit
        if limit:
            query = query.limit(limit)
        return query

    @property
    def actions(self):
        actions = []
        for action in self.available_actions:
            action = action.copy()
            action['route'] = route = action['url']
            if not route_permitted(route, self.request):
                continue
            action['url'] = route_url(route, self.request)
            actions.append(action)
        return actions

    @property
    def available_years(self):
        year = self.start_year
        now = datetime.datetime.now()
        current = now.year
        if now.month >= 8:
            current += 1
        selected = get_selected_year()
        result = []
        while year <= current:
            data = {'year': year}
            if year == selected:
                data['selected'] = 'selected'
            result.append(data)
            year += 1
        return result

    def __call__(self):
        result = []
        columns = self.table_columns
        for line in self.data():
            new_line = []
            for i, key in enumerate(line.keys()):
                formatter = self.query.formatters.get(key)
                value = line[i]
                if formatter:
                    value = formatter(value, request=self.request)
                new_line.append(
                    {'value': value, 'css_class': columns[i]['css_class']})
            result.append(new_line)
        data = {'data': result,
                'header': columns,
                'actions': self.actions,
                'records': len(result)}
        if self.year_selection:
            data['years'] = self.available_years
        return {'status': 'success', 'data': data}


class PrintBaseView(object):

    filename = NotImplemented

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_json(self, obj):
        data = json.loads(json.dumps(obj))
        if 'day' in data:
            data['day'] = date_time(parse_date(data['day']))
        return data

    def __call__(self):
        pdf = self.get_pdf()
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = 'application/pdf'
        response.content_disposition = (
            'attachment; filename=%s.pdf' % self.filename)
        response.app_iter = FileIter(pdf)
        return response


class CSVImporterView(View):

    charset = 'utf-8'

    def _import(self, file, max=99999):
        file = StringIO(file.getvalue().decode(self.charset))
        reader = csv.reader(file, delimiter=';')
        count = 0
        for line in reader:
            if count == 0:
                count += 1
                continue
            if count >= max:
                return
            try:
                self.add_data(line)
            except Exception as e:
                transaction.abort()
                return {'status': 'error', 'message': str(e)}
            count += 1
        count -= 1
        return {'status': 'success',
                'message': '%s Mitglieder importiert.' % count}

    def __call__(self):
        if not self.form_submit():
            return {'status': 'success', 'data': {}}
        file = self.request.params.get('file').file
        file.seek(0)
        return self._import(file)


class CSVExporterView(View):

    @property
    def db(self):
        import zope.component
        import risclog.sqlalchemy.interfaces
        return zope.component.getUtility(
            risclog.sqlalchemy.interfaces.IDatabase)

    def _data(self, query):
        return query.all()

    @property
    def data(self):
        file_ = StringIO()
        writer = csv.writer(file_, delimiter=';', dialect='excel')
        query = self.query()
        query = query.filter(
            getattr(query._select_from_entity.columns,
                    'organization_id') ==
            self.request.user.organization_id)
        writer.writerow([d['name'] for d in query.column_descriptions])
        for member in self._data(query):
            writer.writerow(member)
        return file_.getvalue().encode('utf-8')

    def __call__(self):
        data = self.data
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = 'text/comma-separated-values'
        response.content_length = len(data)
        response.content_disposition = (
            'attachment; filename=%s.csv' % self.filename)
        response.app_iter = FileIter(BytesIO(data))
        return response


class XLSXImporterView(View):

    def _import(self, file):
        wb = openpyxl.load_workbook(file, data_only=True)
        sheet = wb.get_active_sheet()
        for index, line in enumerate(sheet.rows):
            if index in (0, 1):
                continue
            self.add_data(line)
        return {'status': 'success',
                'message': '%s Daten mimportiert.' % index}

    def __call__(self):
        if not self.form_submit():
            return {'status': 'success', 'data': {}}
        file = self.request.params.get('file').file
        file.seek(0)
        return self._import(file)


class XLSXExporterView(View):

    title = NotImplemented
    currency_format = '#,##0.00 [$€-407];-#,##0.00 [$€-407]'
    decimal_format = '#,##0.0'
    percent_format = '0.00%'
    date_format = 'dd.mm.yy'
    sheet_title = 'Datenbank Export'

    @property
    def db(self):
        import zope.component
        import risclog.sqlalchemy.interfaces
        return zope.component.getUtility(
            risclog.sqlalchemy.interfaces.IDatabase)

    @property
    def headline(self):
        return '{}, {} - {} - {}'.format(
            self.sheet_title, self.request.user.username,
            date_time(datetime.datetime.now()), self.title)

    @property
    def _query(self):
        query = self.query()
        return query.filter(
            getattr(query._select_from_entity.columns,
                    'organization_id') ==
            self.request.user.organization_id)

    @property
    def headers(self):
        return [d['name'] for d in self._query.column_descriptions]

    def _data(self, query):
        return query.all()

    def export_helper(self):
        data = self._data(self._query)
        for column_index, cell in enumerate(self.headers):
            self.worksheet.write(1, column_index, cell, self.bold_style)

        for row_index, row in enumerate(data):
            for column_index, cell in enumerate(row):
                self.write_cell(row_index, column_index, cell)

    def write_cell(self, row, column, cell):
        style = {}
        value = cell

        if isinstance(cell, tuple):
            value, style = cell

        if (isinstance(value, datetime.date) or
                isinstance(value, datetime.datetime)):
            style.update({'num_format': self.date_format})
        elif isinstance(value, str) and '€' in value:
            style.update({'num_format': self.currency_format})
        elif isinstance(value, str) and '%' in value:
            value = value / 100
            style.update({'num_format': self.percent_format})
        elif isinstance(value, bool):
            value = boolean(value)
        elif isinstance(value, int):
            style.update({'num_format': '0'})
        elif isinstance(value, float):
            style.update({'num_format': self.decimal_format})

        if style:
            self.worksheet.write(
                row+2, column, value, self.workbook.add_format(style))
        else:
            self.worksheet.write(row+2, column, value)

    def after_export(self):
        return

    def export(self):
        result = BytesIO()
        self.workbook = xlsxwriter.Workbook(result, {'in_memory': True})
        self.worksheet = self.workbook.add_worksheet(self.sheet_title)
        self.bold_style = self.workbook.add_format({'bold': True})

        # Write headline and merge cells
        self.worksheet.merge_range(0, 0, 0, len(self.headers)-1, '')
        self.worksheet.write(
            0, 0, self.headline, self.workbook.add_format({'font_size': 16}))

        self.export_helper()
        self.after_export()

        self.workbook.close()
        result.seek(0)
        return result

    def __call__(self):
        result = self.export()
        response = self.request.response
        response.content_type = 'application/xlsx'
        response.content_disposition = (
            'attachment; filename={}.xlsx'.format(self.filename))
        response.app_iter = FileIter(result)
        return response


class SEPAExporterView(CSVExporterView):

    def format_eur(self, value):
        return format_eur(value)[:-2].replace('.', '').replace(',', '.')

    @property
    def values(self):
        raise NotImplementedError

    def get_member(self, value):
        raise NotImplementedError

    def get_to_pay(self, value):
        raise NotImplementedError

    @property
    def data(self):
        if self.context.is_ueberweisung:
            return self.data_wire_bank
        return self.data_direct_debit

    config = {
        "name": 'Leuna Bungalowgemeinschaft Roter See e.V.',
        "IBAN": 'DE71800537623440000167',
        "BIC": 'NOLADE21HAL',
        "batch": True,
        "creditor_id": 'DE42ZZZ00000348413',
        "currency": "EUR",
    }

    @property
    def data_wire_bank(self):
        sepa = SepaTransfer(self.config, clean=True)
        for value in self.values:
            to_pay = float(self.format_eur(self.get_to_pay(value)))
            member = self.get_member(value)

            if not member.iban:
                continue

            if member.direct_debit_account_holder:
                name = member.direct_debit_account_holder
            elif member.title:
                name = '{} {}, {}'.format(member.lastname, member.title,
                                          member.firstname)
            else:
                name = '{}, {}'.format(member.lastname, member.firstname)

            bd = datetime.date(*(int(s) for s in self.booking_day.split('-')))
            sepa.add_payment({
                "name": name,
                "IBAN": member.iban,
                "BIC": member.bic,
                "amount": int(to_pay * 100),
                "execution_date": bd,
                "description": self.subject
            })

        return sepa.export(validate=True)

    @property
    def data_direct_debit(self):
        sepa = SepaDD(self.config, schema="pain.008.001.02", clean=True)
        payment_id = (
            self.context.pmtinfid or 'PII0ad20386aa6c4287ba8e2000c25c01e2')

        for value in self.values:
            to_pay = float(self.format_eur(self.get_to_pay(value)))
            if to_pay <= 0:
                continue

            member = self.get_member(value)

            if not member.direct_debit or not member.iban:
                continue

            id_ = '{}{}'.format(member.lastname, '/'.join(
                str(m.number) for m in member.allotments))

            if member.direct_debit_account_holder:
                name = member.direct_debit_account_holder
            elif member.title:
                name = '{} {}, {}'.format(member.lastname, member.title,
                                          member.firstname)
            else:
                name = '{}, {}'.format(member.lastname, member.firstname)

            bd = datetime.date(*(int(s) for s in self.booking_day.split('-')))
            sepa.add_payment({
                "name": name,
                "IBAN": member.iban,
                "BIC": member.bic,
                "amount": int(to_pay * 100),  # in cents
                "type": "RCUR",  # FRST,RCUR,OOFF,FNAL
                "collection_date": bd,
                "mandate_id": id_,
                "mandate_date": datetime.date.today(),
                "description": self.subject,
                "endtoend_id": payment_id,
            })

        return sepa.export(validate=True)

    def __call__(self):
        response = self.request.response
        response.content_type = 'application/xml'
        response.content_disposition = (
            'attachment; filename={}.xml'.format(self.filename))
        response.app_iter = FileIter(BytesIO(self.data))
        return response
