# encoding: utf-8
from sw.allotmentclub import DashboardData
from pyramid.view import view_config
import sw.allotmentclub.browser.base
import sw.allotmentclub.browser.login
import time


@view_config(route_name='dashboard', renderer='json',
             permission='view')
class DashboardListView(sw.allotmentclub.browser.base.View,
                        sw.allotmentclub.browser.login.NetatmoMixin):

    temperature_data = (
        ('luefter_aussenluft', 'Aussenluft', '#E24913', '{} °C'),
        ('luefter_zuluft', 'Zuluft', '#6595b4', '{} °C'),
        ('luefter_fortluft', 'Fortluft', '#FF9F01', '{} °C'),
        ('luefter_abluft', 'Abluft', '#7e9d3a', '{} °C'),
        ('luefter_abluft_feuchte', 'Abluft Feuchte', '#7e9d3a', '{} %'),
        ('luefter_percent', 'Lüfterstufe', '#BD362F', '{} %'),
    )

    plot_data = ('luefter_aussenluft', 'luefter_zuluft', 'luefter_fortluft',
                 'luefter_abluft')

    def update(self):
        result = dict(temperatures=[], plots=[])
        for i, d in enumerate(
                DashboardData.query()
                .order_by(DashboardData.date.desc()).limit(576)):
            unixtime = time.mktime(d.date.timetuple()) * 1000
            if i == 0:
                result['date'] = d.date.strftime('am %d.%m.%Y um %H:%M Uhr')
                for k, title, color, fmt in self.temperature_data:
                    result['temperatures'].append(dict(
                        title=title,
                        color=color,
                        current_value=getattr(d, k),
                        tendency='',
                        current_value_str=fmt.format(getattr(d, k))))
                    result['plots'].append([])
            if i == 1:
                for j, (k, title, color, fmt) in enumerate(
                        self.temperature_data):
                    tendency = 'right'
                    if (result['temperatures'][j]['current_value'] <
                            getattr(d, k)):
                        tendency = 'down'
                    elif (result['temperatures'][j]['current_value'] >
                            getattr(d, k)):
                        tendency = 'up'
                    result['temperatures'][j]['tendency'] = tendency

            for j, k in enumerate(self.plot_data):
                result['plots'][j].insert(0, [unixtime, getattr(d, k)])
        result['temp'] = self.get_temp_data(dest='wachtelberg')
        self.result = dict(data=result, status='success')
