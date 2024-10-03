from fastapi import APIRouter,status, Depends
from database import Session, engine
from schemas import SignUpModel, LoginModel
from model import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from starlette import status
from config import Settings
from fastapi.openapi.models import SecurityScheme, OAuthFlows

auth_router=APIRouter(prefix='/auth',tags=['auth'])

session=Session(bind=engine)
 
@AuthJWT.load_config
def get_config():
    return Settings()

@auth_router.get('/') 
async def hello(Authrize:AuthJWT=Depends()):
    """ 
        ##  Simple Hello Word for Auth_router
        This route is used to to display Hello World.
        
    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid Token')
    return {'Message': 'Hello World'}


@auth_router.post('/signup', response_model=SignUpModel, status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    
    """ 
        ##  SIGN-UP USER
        This route is used to create new users.
        Following details required:-        
        - Username :  String
        - Email:  String
        - Password:  String
        - Is_staf:  Bool
        - Is_active:  Bool
        
    """
    # Check if the email already exists
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    # Check if the username already exists
    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exists")

    # Create a new user and hash the password
    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    # Add the new user to the session and commit
    session.add(new_user)
    session.commit()

    # Refresh the session to get the user with the newly created ID
    session.refresh(new_user)

    # Return a dictionary representation of the Pydantic model
    return {
        "id": new_user.id,
        "username": new_user.username,
        "password": new_user.password,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "is_staff": new_user.is_staff
    }


#Login Routs

@auth_router.post('/login',status_code=200)
async def login(user: LoginModel, Authorize: AuthJWT= Depends()):
    
    """ 
        ##  LOG-IN USER
        This route is used for login users.
        - Return's Access Token and Refresh Token
        Following details required:-        
        - Username :  String
        - Password:  String
        
    """
    db_user= session.query(User).filter(User.username==user.username).first()
    if db_user and check_password_hash(db_user.password, user.password ):
        print(db_user , check_password_hash(db_user.password, user.password ))
        access_token= Authorize.create_access_token(subject=db_user.username)
        print(access_token)
        refresh_token=Authorize.create_refresh_token(subject=db_user.username) 
        print(access_token)
        response={'access': access_token,'refresh':refresh_token}
        print(response)
        return jsonable_encoder(response)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid Username or Password')

#Refresh
@auth_router.get("/refresh")
async def refresh_token(Authrize:AuthJWT=Depends()):
    """ 
        ##  CREATE FRESH TOKEN
        This route is used to create fresh token.
        Following details required:-        
        - Refresh Token :  String
        
    """
    try:
        Authrize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Please provide Valid Refresh Token")
    current_user = Authrize.get_jwt_subject()
    access_token=Authrize.create_access_token(subject=current_user)
    return {'access':access_token,}


@auth_router.delete('/delete/user/{id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id:int,Authrize:AuthJWT=Depends()):
    """ 
        ##  DELETE ORDER
        This route is used to delete an order by its ID.
        
    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid Token ")
    username=Authrize.get_jwt_subject()
    current_user=session.query(User).filter(User.username==username).first()
    if current_user.is_staff:
        user_to_delete=session.query(User).filter(User.id==id).first()
        if user_to_delete.is_staff:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST,detail="You are not delete another Super User ") 
            
        session.delete(user_to_delete)
        session.commit()
        return user_to_delete
    raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST,detail="You are not Autherized to delete any User ")  
    