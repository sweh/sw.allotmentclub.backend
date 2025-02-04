"""Add email to members.

Revision ID: 2cb8d240d5ac
Revises: 4e4d0ae80e7a
Create Date: 2015-03-02 15:07:38.712318

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2cb8d240d5ac"
down_revision = "4e4d0ae80e7a"


def upgrade():
    op.add_column(
        "member", sa.Column("email", sa.String(length=100), nullable=True)
    )
    op.execute("""UPDATE member SET email = 'sebastian.wehrmann@icloud.com'
                  WHERE id = 76;""")
    op.execute(
        "UPDATE member SET email = 'stephan.leuna@t-online.de' WHERE id = 85;"
    )
    op.execute("UPDATE member SET email = 'andre_atb@msn.com' WHERE id = 86;")
    op.execute("UPDATE member SET email = 'kalovo39@gmx.de' WHERE id = 89;")
    op.execute("UPDATE member SET email = 'smjala@aim.com' WHERE id = 90;")
    op.execute("UPDATE member SET email = 'olaf.kuehn@gmx.net' WHERE id = 91;")
    op.execute("UPDATE member SET email = 's.kern@ivh.de' WHERE id = 100;")
    op.execute(
        "UPDATE member SET email = 'amielke@primacom.net' WHERE id = 101;"
    )
    op.execute("""UPDATE member SET email = 'j.sonntag@leipziger-messe.de'
                  WHERE id = 103;""")
    op.execute(
        "UPDATE member SET email = 'harry.noglik@t-online.de' WHERE id = 105;"
    )
    op.execute("""UPDATE member SET email = 'lochau.hartmann@freenet.de'
                  WHERE id = 118;""")
    op.execute("UPDATE member SET email = 'morki1@hotmail.de' WHERE id = 123;")
    op.execute(
        "UPDATE member SET email = 'boehme.wsf@t-online.de' WHERE id = 126;"
    )
    op.execute(
        "UPDATE member SET email = 'juergen.liehm@web.de' WHERE id = 127;"
    )
    op.execute("""UPDATE member SET email = 'roesler@informatik.uni-halle.de'
                  WHERE id = 129;""")
    op.execute(
        "UPDATE member SET email = 'super_bingo@freenet.de' WHERE id = 133;"
    )
    op.execute(
        "UPDATE member SET email = 'spiess.dietmar@web.de' WHERE id = 134;"
    )
    op.execute(
        "UPDATE member SET email = 'eberhard.kietz@online.de' WHERE id = 135;"
    )
    op.execute("""UPDATE member SET email = 'peter.reinhold@superkabel.de'
                  WHERE id = 141;""")
    op.execute(
        "UPDATE member SET email = 'tee.mueller@t-online.de' WHERE id = 142;"
    )
    op.execute("UPDATE member SET email = 'b.e.bochi@gmx.de' WHERE id = 149;")
    op.execute("UPDATE member SET email = 'ominette@gmx.de' WHERE id = 150;")
    op.execute("UPDATE member SET email = 'dr.kobelt@gmx.de' WHERE id = 156;")
    op.execute(
        "UPDATE member SET email = 'r.lichtenfeld@freenet.de' WHERE id = 157;"
    )
    op.execute(
        "UPDATE member SET email = 'basteu@t-online.de' WHERE id = 158;"
    )
    op.execute(
        "UPDATE member SET email = 'angela_maxis@arcor.de' WHERE id = 164;"
    )
    op.execute(
        "UPDATE member SET email = 'gerd-wmi@t-online.de' WHERE id = 165;"
    )
    op.execute(
        "UPDATE member SET email = 'uwe.reinicke@epc.com' WHERE id = 167;"
    )
    op.execute(
        "UPDATE member SET email = 'fischereddager@aol.com' WHERE id = 171;"
    )
    op.execute(
        "UPDATE member SET email = 'beritschmidt@arcor.de' WHERE id = 173;"
    )
    op.execute(
        "UPDATE member SET email = 'klaus-hertwig@online.de' WHERE id = 174;"
    )
    op.execute(
        "UPDATE member SET email = 'GuenterTillack@aim.com' WHERE id = 185;"
    )
    op.execute(
        "UPDATE member SET email = 'schloeffel_h@t-online.de' WHERE id = 186;"
    )


def downgrade():
    op.drop_column("member", "email")
