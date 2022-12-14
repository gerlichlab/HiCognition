from werkzeug.security import generate_password_hash
from sqlalchemy import select
from app.models import *
from app.database import session
import app.database as db

class BaseDAO:
    def __init__(self, model):
        self.model = model
         
    def get_all(self):
        return db.session.query(self.model).all()
        
    def get_by_id(self, id: int):
        return db.session.query(self.model).filter_by(id=id).first()
    
    def add(self, obj):
        if isinstance(obj, self.model):
            db.session.add(obj)
            return True
    def delete(self, obj):
        if isinstance(obj, self.model):
            db.session.delete(obj)
            return True

class UserDAO(BaseDAO):
    def get_by_name(self, username: str):
        return db.session.query(self.model).filter_by(username=username).first()

    def get_by_email(self, email: str):
        return db.session.query(self.model).filter_by(email=email).first()

class PhysicalFileDAO(BaseDAO):
    def get_by_hash(self, md5: str):
        return db.session.query(self.model).filter_by(md5=md5).first()
    
class FileDAO(BaseDAO):
    def get_by_hash_userid(self, md5: str, user_id: int):
        return db.session.query(self.model).filter_by(md5=md5, user_id=user_id).first()

# class DirectoryDAO(BaseDAO):
#     pass

class BaseFeatureSetDAO(BaseDAO):
    def get_by_name(self, name: str):
        return db.session.query(self.model).filter_by(name=name).first()
        
class CalculationDAO(BaseDAO):
    pass

class TaskDAO(BaseDAO):
    def get_by_job_id(self, id: int):
        raise NotImplementedError
    
    def get_running(self):
        raise NotImplementedError
    
    def get_failed(self):
        raise NotImplementedError
    
    def get_finished(self):
        raise NotImplementedError

user_dao = UserDAO(User)
file_dao = FileDAO(File)
physicalfile_dao = PhysicalFileDAO(PhysicalFile)
# dir_dao = DirectoryDAO(Directory)
regionset_dao = BaseFeatureSetDAO(RegionSet)
feature1d_dao = BaseFeatureSetDAO(Feature1D)
feature2d_dao = BaseFeatureSetDAO(Feature2D)

linegraphcalculation_dao = CalculationDAO(LinegraphCalculation)
lolacalculation_dao = CalculationDAO(LolaCalculation)
umap1Dcalculation_dao = CalculationDAO(Umap1DCalculation)
umap2Dcalculation_dao = CalculationDAO(Umap2DCalculation)
stackedlineprofilecalculation_dao = CalculationDAO(StackedLineprofileCalculation)
heatmapcalculation_dao = CalculationDAO(HeatmapCalculation)

task_dao = TaskDAO(Task)