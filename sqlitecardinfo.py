import sqlite3
conn = sqlite3.connect('cardinfo.db')
c = conn.cursor()

# change index
#c.execute("UPDATE cards SET printid=?", (0,))


#c.execute("SELECT * FROM cards WHERE series='Batman'")
#c.execute("SELECT * FROM cards")
#print(c.fetchall())
# Joker, Batman, 1, joker.jpg,
# Batman, Batman, 1, batman.jpg,
# Robin, Batman, 1, robin.jpg,

#c.execute("SELECT * FROM cardinfo")
#c.execute("DELETE from cardinfo")
#c.execute("DROP TABLE cardinfo")

# c.execute("""CREATE TABLE cardinfo (
#     character text,
#     series text,
#     wishlist int,
#     totalclaim int,
#     totalgenerated int
#     )""")

#c.execute("INSERT INTO cards VALUES ('Batman','Batman',1,'batman.jpg')")
#c.execute("INSERT INTO cards VALUES ('Tarik','CSGO',0,'tarik.png')")

conn.commit()

conn.close()