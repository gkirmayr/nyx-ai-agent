import sqlite3

def criar_conexao():
    conn = sqlite3.connect("banco_videos.db")
    return conn

def setup_database(conexao):
    cursor = conexao.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        data_entrega TEXT,
        status TEXT,
        plataforma TEXT
    )
    """ 
    cursor.execute(query)
    conexao.close()



if __name__ == "__main__":
    conexao = criar_conexao()

    setup_database(conexao)
    print("Banco de dados criado com sucesso!")
    
    
