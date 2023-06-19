"""Add new accounts

Revision ID: 48303c2cf2eb
Revises: e927a9a287ad
Create Date: 2023-06-19 07:53:42.089315

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '48303c2cf2eb'
down_revision = 'e927a9a287ad'


def upgrade():
    # signature = pkg_resources.resource_stream(
    #     'sw.allotmentclub.signatures', 'rw.png').read()
    # signature = 'data:application/png;base64,{}'.format(
    #     base64.b64encode(signature).decode('utf-8'))
    signature = ''
    op.execute("""
INSERT into public.user
    (id, username, password, unrestricted_access, vorname, nachname, anrede,
     handynummer, ort, position, signature, email, organization_id)
VALUES
    (6, 'rw', '{pw}', true, 'Ronny', 'Weber', 'Herr', '0173 2713035',
     'Leipzig', 'Stellvertretender Vorsitzender', '{signature}',
     'ronnyweber11@aol.com', 1)
""".format(pw='$2a$12$23Lz6/ozpjpMd0NMxGWfa.dcGHG6/6gHptb8c7U5TLDXXElW6RZ96',
           signature=signature))

    op.execute("""
INSERT into public.user
    (id, username, password, unrestricted_access, vorname, nachname, anrede,
     handynummer, ort, position, signature, email, organization_id)
VALUES
    (8, 'ms', '{pw}', false, 'Matthias', 'Schulz', 'Herr', '0152 26346780',
     'Bad Lauchstädt', 'Schatzmeister', '', 'matthias.schulz82@gmail.com', 1)
""".format(pw='$2a$12$nFSJLH7MVmUPqw4TZLz9uO2eAhvyEGOceLiT7BdaqMkNltRcY7x3e'))

    op.execute("""
UPDATE public.user SET is_locked = 'Zurückgetreten' WHERE username = 'hs'""")
    op.execute("""
UPDATE public.user SET is_locked = 'Zurückgetreten' WHERE username = 'ar'""")
    op.execute("""
UPDATE public.user SET position = 'Vorsitzende', unrestricted_access = true
WHERE username = 'ah'""")
    op.execute("UPDATE accessauthority SET user_id = 8 WHERE user_id = 41")


def downgrade():
    op.execute("UPDATE public.user SET is_locked = null WHERE username = 'hs'")
    op.execute("UPDATE public.user SET is_locked = null WHERE username = 'ar'")
    op.execute("""\
UPDATE public.user SET position = 'Schatzmeister',
unrestricted_access = false WHERE username = 'ah'""")
    op.execute("UPDATE accessauthority SET user_id = 41 WHERE user_id = 8")
    op.execute("DELETE FROM log WHERE user_id in (6, 8);")
    op.execute("DELETE FROM public.user WHERE username = 'ms';")
    op.execute("DELETE FROM public.user WHERE username = 'rw';")
