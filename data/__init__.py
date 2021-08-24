from sqlalchemy import create_engine

USER = "root"
PW = "mypass"
IP = "127.0.0.1"
PORT = "3306"
DB = "coins"

engine = create_engine(f"mysql+pymysql://{USER}:{PW}@{IP}:{PORT}/{DB}")
