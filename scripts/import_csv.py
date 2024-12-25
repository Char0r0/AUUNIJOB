import pandas as pd
from config.database import SessionLocal, engine
from models.job import Base, Job
import logging
from sqlalchemy.exc import SQLAlchemyError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='database_import.log'
)

def import_csv_to_db():
    # 创建数据库表
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("数据库表创建成功")
    except SQLAlchemyError as e:
        logging.error(f"创建数据库表时出错: {str(e)}")
        return
    
    try:
        # 从 job_data.csv 读取
        df = pd.read_csv('tables/job_data.csv')
        logging.info(f"成功读取CSV文件，共 {len(df)} 条记录")
    except Exception as e:
        logging.error(f"读取CSV文件时出错: {str(e)}")
        return
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 清空 jobs 表
        db.query(Job).delete()
        db.commit()
        logging.info("已清空 jobs 表中的旧数据")

        # 遍历CSV数据并插入数据库
        for index, row in df.iterrows():
            db_job = Job(
                job_title=row['Job Title'],
                uni_name=row['UniName'],
                link=row['Link']
            )
            db.add(db_job)
            logging.info(f"添加新职位: {row['Job Title']}")
                
            if index % 100 == 0:  # 每100条记录提交一次
                db.commit()
                logging.info(f"已处理 {index} 条记录")
        
        # 最后提交剩余的记录
        db.commit()
        logging.info("所有数据导入成功！")
        
    except SQLAlchemyError as e:
        logging.error(f"数据库操作出错: {str(e)}")
        db.rollback()
    except Exception as e:
        logging.error(f"导入过程出错: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_csv_to_db() 