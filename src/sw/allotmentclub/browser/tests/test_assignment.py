# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import transaction
import mock


def setUp():
    from sw.allotmentclub import Assignment, AssignmentAttendee, Member
    member = Member.create(firstname='Gerd', lastname='Mittag')
    ass = Assignment.create(day=datetime.datetime(2015, 3, 7, 9),
                            purpose='Frühjahrsputz',
                            responsible=member,
                            accounting_year=2015)
    AssignmentAttendee.create(
        assignment=ass, member=member, hours=4)
    transaction.commit()
    return member, ass


def test_assignments_can_have_attendees(database):
    member, assignment = setUp()
    from sw.allotmentclub import AssignmentAttendee
    assert 1 == len(assignment.attendees)
    assert 1 == len(member.assignments)
    AssignmentAttendee.create(assignment=assignment, member=member, hours=4)
    assert 2 == len(assignment.attendees)
    assert 2 == len(member.assignments)


def test_AssignmentListView_1(browser, json_fixture):
    """It displays list of assignments."""
    url = json_fixture.url()
    setUp()
    browser.login()
    browser.open('http://localhost{}'.format(url))
    json_fixture.assertEqual(browser.json, 'data')


def test_AssignmentAddView_1(browser, json_fixture):
    """It can add new assignments via JSON."""
    from sw.allotmentclub import Assignment
    url = json_fixture.url()
    browser.login()
    with mock.patch('sw.allotmentclub.browser.assignment.datetime_now') as now:
        current_year = datetime.datetime.now().year
        now.return_value = datetime.datetime(current_year, 2, 20, 10)
        browser.post('http://localhost{}'.format(url), data='')
    assert 'success' == browser.json['status']
    json_fixture.assertEqual(browser.json, 'data')
    assert 1 == len(Assignment.query().all())


def test_AssignmentAttendeesEditView_1(browser, json_fixture):
    """It can handle german floats for assignment hours."""
    from sw.allotmentclub import AssignmentAttendee
    url = json_fixture.url()
    setUp()
    browser.login()
    browser.post('http://localhost{}'.format(url), data={'hours': '2,5'})
    assert 'success' == browser.json['status']
    assert 2.5 == AssignmentAttendee.get(1).hours


def test_AssignmentListAttendeesView_1(browser, json_fixture):
    """It can display list of assignment attendees."""
    url = json_fixture.url()
    setUp()
    browser.login()
    browser.open('http://localhost{}'.format(url))
    json_fixture.assertEqual(browser.json, 'data')


def test_AssignmentDeleteAttendeesView_1(browser, json_fixture):
    """It can delete assignment attendees from assignment."""
    url = json_fixture.url('/assignments/1/attendees/1/delete')
    setUp()
    browser.login()
    browser.open('http://localhost{}'.format(url))
    json_fixture.assertEqual(browser.json, 'data')
    browser.open('http://localhost/assignments/1/list')
    assert [] == browser.json_result


def test_AssignmentTodoListView_1(browser, json_fixture):
    """It displays list of assignment todos."""
    url = json_fixture.url()
    setUp()
    browser.login()
    browser.open('http://localhost{}'.format(url))
    json_fixture.assertEqual(browser.json, 'data')


def test_AssignmentTodoAddView_1(browser, json_fixture):
    """It can add new assignment todos via JSON."""
    from sw.allotmentclub import AssignmentTodo
    url = json_fixture.url()
    browser.login()
    browser.post('http://localhost{}'.format(url), data='')
    assert 'success' == browser.json['status']
    json_fixture.assertEqual(browser.json, 'data', save=True)
    assert 1 == len(AssignmentTodo.query().all())
    assert 4 == AssignmentTodo.query().one().priority
