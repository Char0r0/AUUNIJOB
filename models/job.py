from sqlalchemy import Column, Integer, String, DateTime
from config.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String)
    uni_name = Column(String)
    link = Column(String) 