import os
import sys
import logging
import concurrent.futures
import pandas as pd
from datetime import datetime
import subprocess

# 获取项目根目录的绝对路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录添加到 Python 路径
sys.path.append(ROOT_DIR)

# 现在可以导入项目模块
from config.database import SessionLocal, engine
from models.job import Base, Job
from sqlalchemy.exc import SQLAlchemyError

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - INFO - %(message)s',
    filename='job_scraper.log'
)

def import_to_db(csv_path):
    """将CSV数据导入到数据库"""
    try:
        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        logging.info("数据库表创建成功")
        
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        logging.info(f"成功读取CSV文件，共 {len(df)} 条记录")
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 清空现有数据
            db.query(Job).delete()
            db.commit()
            logging.info("已清空现有数据")
            
            # 导入新数据
            for index, row in df.iterrows():
                db_job = Job(
                    job_title=row['Job Title'],
                    uni_name=row['UniName'],
                    link=row['Link']
                )
                db.add(db_job)
                
                if index % 100 == 0:
                    db.commit()
                    logging.info(f"已处理 {index} 条记录")
            
            # 提交剩余记录
            db.commit()
            logging.info("所有数据导入成功！")
            
        except Exception as e:
            logging.error(f"数据库操作出错: {str(e)}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        logging.error(f"导入过程出错: {str(e)}")

def run_scraper(scraper_file):
    try:
        scraper_path = os.path.join(ROOT_DIR, 'scrapers', scraper_file)
        module_name = scraper_file[:-3]
        
        result = subprocess.run(['python3', scraper_path], 
                             capture_output=True, 
                             text=True)
        
        if result.returncode == 0:
            logging.info(f"Successfully ran {module_name}")
            return True
        else:
            logging.error(f"Error running {module_name}: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"Error in {scraper_file}: {str(e)}")
        return False

def run_scrapers():
    logging.info("Starting parallel job scraping program...")
    
    scrapers_dir = os.path.join(ROOT_DIR, 'scrapers')
    scraper_files = [f for f in os.listdir(scrapers_dir) 
                    if f.endswith('.py') and f != '__init__.py']
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(run_scraper, scraper_files))
    
    try:
        all_data = []
        tables_dir = os.path.join(ROOT_DIR, 'tables')
        os.makedirs(tables_dir, exist_ok=True)
        
        output_path = os.path.join(tables_dir, 'job_data.csv')
        if os.path.exists(output_path):
            os.remove(output_path)
            logging.info(f"Deleted old {output_path}")

        for file in os.listdir(tables_dir):
            if file.endswith('.csv'):
                file_path = os.path.join(tables_dir, file)
                df = pd.read_csv(file_path)
                all_data.append(df)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df.to_csv(output_path, index=False)
            logging.info(f"Combined data saved to {output_path}")
            
            # 导入数据到数据库
            import_to_db(output_path)
        else:
            logging.warning("No data to combine")
            
    except Exception as e:
        logging.error(f"Error combining CSV files: {str(e)}")

if __name__ == "__main__":
    run_scrapers()
