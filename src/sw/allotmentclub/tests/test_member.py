def test_member_active_passive(database):
    from sw.allotmentclub import Member, Allotment

    member = Member.create()

    assert member.active is False

    Allotment.create(member=member)

    assert member.active is True
