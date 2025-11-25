import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS core_project")
conn.commit()
conn.close()

print("Tabela core_project removida com sucesso!")
