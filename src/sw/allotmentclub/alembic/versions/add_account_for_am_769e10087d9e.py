"""add account for am.

Revision ID: 769e10087d9e
Revises: fd9f9588878d
Create Date: 2017-06-19 14:02:23.740567

"""
from alembic import op
import pkg_resources
import base64

# revision identifiers, used by Alembic.
revision = '769e10087d9e'
down_revision = 'fd9f9588878d'


def upgrade():
    signature = pkg_resources.resource_stream(
        'sw.allotmentclub.signatures', 'am.png').read()
    signature = 'data:application/png;base64,{}'.format(
        base64.b64encode(signature).decode('utf-8'))
    op.execute("""
INSERT into public.user
    (username, password, unrestricted_access, vorname, nachname, anrede,
     handynummer, ort, position, signature, email, organization_id)
VALUES
    ('am', '{pw}', false, 'Andreas', 'Mielke', 'Herr', '0160 1546148',
     'Naumburg', 'Schriftführer', '{signature}', 'amielke@primacom.net', 1)
""".format(pw='$2b$12$mi1JV2RA/hvmkQVVv2Uube4ODAX44LOsmMXvkwLUVlIzKS18P0eve',
           signature=signature))

    op.execute("""
INSERT into public.user
    (username, password, unrestricted_access, vorname, nachname, anrede,
     handynummer, ort, position, signature, email, organization_id)
VALUES
    ('cs', '{pw}', false, 'Constanze', 'Seyfert', 'Frau', '',
     '', 'Revisionskommission', '', '', 1)
""".format(pw='$2b$12$i8SjfxgMnw464DAyFJEipeXswIvtC.OcrSGYYZ/PBAC97NvJus0ou'))

    op.execute("""
UPDATE public.user SET is_locked = 'Zurückgetreten' WHERE username = 'ks'""")
    op.execute("""
UPDATE public.user SET position = 'Datenbank-Beauftragter'
WHERE username = 'sw'""")
    op.execute("""
UPDATE public.user SET position = 'Vorsitzender'
WHERE username = 'hs'""")
    op.execute("""
UPDATE public.user SET position = 'Stellvertretende Vorsitzende'
WHERE username = 'ar'""")


def downgrade():
    op.execute("DELETE FROM public.user WHERE username = 'am';")
    op.execute("DELETE FROM public.user WHERE username = 'cs';")
