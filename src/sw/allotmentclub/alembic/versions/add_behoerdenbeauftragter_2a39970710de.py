"""Add behoerdenbeauftragter

Revision ID: 2a39970710de
Revises: e0985a4462d3
Create Date: 2017-09-20 13:57:49.620450

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "2a39970710de"
down_revision = "e0985a4462d3"


def upgrade():
    # signature = pkg_resources.resource_stream(
    #     'sw.allotmentclub.signatures', 'ek.png').read()
    # signature = 'data:application/png;base64,{}'.format(
    #     base64.b64encode(signature).decode('utf-8'))
    signature = None
    op.execute(
        """
INSERT into public.user
    (username, password, unrestricted_access, vorname, nachname, anrede,
     handynummer, ort, position, signature, email, organization_id)
VALUES
    ('ek', '{pw}', false, 'Dr. Eberhard', 'Kietz', 'Herr', '0351 4708959',
     'Dresden', 'Behördenbeauftragter', '{signature}',
     'eberhard.kietz@online.de', 1)
""".format(
            pw="$2b$12$6gfMaN3CX2soj2YAh5qk2.yCpVAG6I0QNJAEuKSDs18A3XZFLYXDq",
            signature=signature,
        )
    )


def downgrade():
    op.execute("DELETE FROM public.user WHERE username = 'ek'")
