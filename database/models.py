from sqlalchemy import Column, Integer, String, DateTime, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class JobType(enum.Enum):
    ACADEMIC = "academic"
    RESEARCH = "research"
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"
    ADMINISTRATIVE = "administrative"

class EmploymentType(enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CASUAL = "casual"
    CONTRACT = "contract"

class JobListing(Base):
    __tablename__ = 'job_listings'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    university = Column(String)
    link = Column(String)
    description = Column(String)
    location = Column(String)
    faculty = Column(String)
    salary_range_min = Column(Float)
    salary_range_max = Column(Float)
    job_type = Column(Enum(JobType))
    employment_type = Column(Enum(EmploymentType))
    closing_date = Column(DateTime)
    created_at = Column(DateTime) 