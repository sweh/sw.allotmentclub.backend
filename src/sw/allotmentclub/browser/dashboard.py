# encoding: utf-8
from sw.allotmentclub import DashboardData
from pyramid.view import view_config
import sw.allotmentclub.browser.base
import time


@view_config(route_name='dashboard', renderer='json',
             permission='view')
class DashboardListView(sw.allotmentclub.browser.base.View):

    plot_data = (
        ('luefter_aussenluft', 'Aussenluft', '#E24913', ''),
        ('luefter_zuluft', 'Zuluft', '#6595b4', ''),
        ('luefter_fortluft', 'Fortluft', '#FF9F01', ''),
        ('luefter_abluft', 'Abluft', '#7e9d3a', ''),
    )

    def update(self):
        result = dict(temperatures=[], plots=[])
        for i, d in enumerate(
                DashboardData.query()
                .order_by(DashboardData.date.desc()).limit(576)):
            unixtime = time.mktime(d.date.timetuple()) * 1000
            if i == 0:
                result['date'] = d.date.strftime('am %d.%m.%Y um %H:%M Uhr')
                for k, title, color, css in self.plot_data:
                    result['temperatures'].append(dict(
                        title=title,
                        color=color,
                        css_class=css,
                        current_value='{} °C'.format(getattr(d, k))))
                    result['plots'].append([])
                result['temperatures'].append(dict(
                    title="Abluft Feuchte",
                    color="#7e9d3a",
                    css_class='',
                    current_value='{} %'.format(d.luefter_abluft_feuchte,
                                                d.luefterstufe)))
                result['temperatures'].append(dict(
                    title="Lüfterstufe",
                    color="#BD362F",
                    css_class='',
                    current_value='{} % ({})'.format(d.luefter_percent,
                                                     d.luefterstufe)))
            for j, (k, title, color, css) in enumerate(self.plot_data):
                result['plots'][j].insert(0, [unixtime, getattr(d, k)])
        self.result = dict(data=result, status='success')
