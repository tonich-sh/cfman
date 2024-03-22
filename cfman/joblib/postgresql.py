
import csv
import io

from cfman.cmdbuilder.commands.postgresql import Psql
from cfman.executor.context import Context


def get_users(ctx: Context) -> list[str]:
    sql = '''COPY (SELECT usename as role_name
FROM pg_catalog.pg_user
ORDER BY role_name) TO stdout (format CSV);'''
    with ctx.belong('postgres'):
        result = ctx.run(Psql().command(sql))
    assert result.ok, result.stderr
    reader = csv.reader(io.StringIO(result.stdout), delimiter=',')
    return {row[0] for row in reader}


def create_user(ctx: Context, username: str, password: str | None):
    # TODO: escape parameters
    sql = f'CREATE USER {username}'
    if password:
        sql += " WITH PASSWORD '{password}'"
    with ctx.belong('postgres'):
        ctx.run(Psql().command(sql + ';'))


def change_password(ctx: Context, username: str, password: str):
    # TODO: escape parameters
    sql = f"ALTER USER {username} WITH PASSWORD '{password}'"
    with ctx.belong('postgres'):
        ctx.run(Psql().command(sql + ';'))


def get_databases(ctx: Context):
    sql = 'COPY (SELECT datname FROM pg_database WHERE datistemplate = false) TO stdout (format CSV)'
    with ctx.belong('postgres'):
        result = ctx.run(Psql().command(sql))
    assert result.ok, result.stderr
    reader = csv.reader(io.StringIO(result.stdout), delimiter=',')
    return {row[0] for row in reader}


def create_database(ctx: Context, database: str, owner: str | None):
    sql = f'CREATE DATABASE {database}'
    if owner:
        sql += f' OWNER {owner}'
    with ctx.belong('postgres'):
        ctx.run(Psql().command(sql + ';'))


def drop_database(ctx: Context, database: str):
    sql = f'DROP DATABASE {database}'
    with ctx.belong('postgres'):
        ctx.run(Psql().command(sql + ';'))


def change_owner(ctx: Context, database: str, owner: str):
    sql = f'ALTER DATABASE {database} OWNER TO {owner}'
    with ctx.belong('postgres'):
        ctx.run(Psql().command(sql + ';'))


def get_tables(ctx: Context, database: str, schema: str | None = None):
    sql = 'SELECT table_schema, table_name FROM information_schema.tables'
    if schema is not None:
        sql += f" WHERE table_schema = '{schema}'"
    sql += ' ORDER BY table_schema, table_name'
    sql_csv = f'COPY ({sql}) TO stdout (format CSV)'
    with ctx.belong('postgres'):
        result = ctx.run(Psql().database(database).command(sql_csv))
    assert result.ok, result.stderr
    reader = csv.reader(io.StringIO(result.stdout), delimiter=',')
    return {(row[0], row[1]) for row in reader}
