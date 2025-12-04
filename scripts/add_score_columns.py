"""Adiciona colunas `team_a_score` e `team_b_score` à tabela tournament_brackets se não existirem."""
import os
import sqlite3
import sys

DB = os.getenv('DATABASE_URL') or 'sqlite:///./test_complete_integration.db'
# Extrai caminho do arquivo de uma URL sqlite:///./file.db
if DB.startswith('sqlite:///'):
    path = DB.replace('sqlite:///', '')
else:
    print('Database URL não é sqlite ou formato inesperado:', DB)
    sys.exit(1)

print('Updating DB file:', path)
conn = sqlite3.connect(path)
cur = conn.cursor()

cur.execute("PRAGMA table_info('tournament_brackets')")
cols = [r[1] for r in cur.fetchall()]
print('Existing columns:', cols)

added = False
if 'team_a_score' not in cols:
    cur.execute("ALTER TABLE tournament_brackets ADD COLUMN team_a_score INTEGER")
    print('Added column team_a_score')
    added = True
if 'team_b_score' not in cols:
    cur.execute("ALTER TABLE tournament_brackets ADD COLUMN team_b_score INTEGER")
    print('Added column team_b_score')
    added = True

if not added:
    print('No columns needed')

conn.commit()
conn.close()
print('Done')
