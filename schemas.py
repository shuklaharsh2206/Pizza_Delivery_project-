from pydantic import BaseModel,BaseSettings
from typing import Optional

class SignUpModel (BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]= False
    is_active: Optional[bool]= True


    class Config:
        from_attributes= True
        json_schema_extra={
            'example':{
                'username':'johndoe',
                'email':'johndoe@gmail.com',
                'password':'password',
                'is_staf':'False',
                'is_active':'True'
            }
        }



class LoginModel(BaseModel):
    username: str
    password: str

class OrderModel(BaseModel):
    
    quantity: int
    
    pizza_size: Optional[str]="SMALL"
    
    
    class Config:   
        from_attributes= True
        json_schema_extra= {
        "example":{
            "quantity": 2,
            "pizza_size":"LARGE"
            
        }
    }
    
class OrderStatusModel(BaseModel):
    order_status: Optional[str]= "PENDING"
    class Config:
        from_attributes= True
        json_schema_extra= {
        "example":{
            "order_status": "PENDING"
          
            
        }
    }