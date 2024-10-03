from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from model import User,Order
from schemas import OrderModel, OrderStatusModel
from database import Session, engine
from fastapi.encoders import jsonable_encoder

order_router=APIRouter(
    prefix='/orders',
    tags=['orders']
)
session=Session(bind=engine)

@order_router.get('/')
async def hello(Authrize:AuthJWT=Depends()):
    
    """
        ## A Sample Hello World Route
        This returns Hello World.

    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid Token ")
    
    
    return {'Message': 'Hello World'}



@order_router.post('/order',status_code=status.HTTP_201_CREATED)
async def place_an_order(order:OrderModel,Authrize:AuthJWT=Depends()):    
    """ 
        ##  PLACING ORDER
        This route is used to place an order.
        Following details required:-        
        - Quantity: Integer     
        - Pizza_size: String

    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid Token ")
    current_user=Authrize.get_jwt_subject()
    
    user=session.query(User).filter(User.username==current_user).first()
    new_order=Order(
        pizza_size= order.pizza_size,
        quantity= order.quantity
    )
    new_order.user=user
    session.add(new_order)
    session.commit()
    
  
    
    return {
        "pizza_size":new_order.pizza_size,
        "quantity": new_order.quantity,
        "id":new_order.id,
        "order_status":new_order.order_status
    }
    
    
@order_router.get("/orders")
async def list_all_orders(Authrize:AuthJWT=Depends()):
    """ 
        ##  List All ORDERS
        This route is used to list all orders.
        Following details required:-        
        - Can ony be accessed by Super User.
        
    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid Token ")
    current_user=Authrize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()
    if user.is_staff:
        orders=session.query(Order).all()
        return jsonable_encoder(orders)
    raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="you are not a super user. ")



@order_router.get("/orders/{id}")
async def get_order_by_id(id:int,Authrize:AuthJWT=Depends()):
    """ 
        ##  LIST ORDERS via ORDER_ID
        This route is used to list order using ORDER_ID.
        Following details required:-        
        - Can ony be accessed by Super User.  
        
    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid Token ")
    user=Authrize.get_jwt_subject()
    current_user=session.query(User).filter(User.username==user).first()
    if current_user.is_staff:
        orders=session.query(Order).filter(Order.id==id).first()
        return jsonable_encoder(orders)
    raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="you are not a super user. ")

    
@order_router.get('/user/orders')
async def get_users_orders(Authrize:AuthJWT=Depends()):
    """ 
        ##  LIST ALL ORDERS OF USER
        This route is used to list all orders of logged-in user.
        
    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid Token ")
    user=Authrize.get_jwt_subject()
    current_user=session.query(User).filter(User.username==user).first()
    
    return jsonable_encoder(current_user.orders)



@order_router.get('/user/order/{id}/')
async def get_specific_order(id: int,Authrize:AuthJWT=Depends()):
    """ 
        ##  GET SPECIFIC ORDER OF USER 
        This route is used to get specific order of logged-in user .
        - Order_id required : Integer
        
    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid Token ")
    user=Authrize.get_jwt_subject()
    current_user=session.query(User).filter(User.username==user).first()
    orders=current_user.orders
    for o in orders:
        if o.id==id:
            return o
    raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST,detail="No Order with such ID ")   
 
 
@order_router.put('/order/update/{order_id}/')
async def update_order(id:int, order:OrderModel,Authrize:AuthJWT=Depends()):
    """ 
        ##  UPDATING PLACED ORDER
        This route is used to update the order details of logged-in user.
        Following details required:-  
        - Order_id: Integer      
        - Quantity: Integer     
        - Pizza_size: String
        
    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid Token ")
    order_to_update=session.query(Order).filter(Order.id==id).first()
    order_to_update.quantity=order.quantity
    order_to_update.pizza_size=order.pizza_size
    
    session.commit()
    response={"id":order_to_update.id,
            "quantity": order_to_update.quantity,
            "pizza_size":order_to_update.pizza_size,
            "order_status":order_to_update.order_status}
    return jsonable_encoder(response)

@order_router.patch('/order/update/{id}/')
async def update_order_status(id:int, order:OrderStatusModel,Authrize:AuthJWT=Depends()):
    """ 
        ## UPDATING ORDER STATUS
        This route is used to update the order_status with the help of order_id.
        Following details required:-        
        - Order_id: Integer     
        - Order_status: String
        - Can only be accessed by Super User
        
    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid Token ")
    username=Authrize.get_jwt_subject()
    current_user=session.query(User).filter(User.username==username).first()
    if current_user.is_staff:
        order_to_update=session.query(Order).filter(Order.id==id).first()
        order_to_update.order_status=order.order_status
        session.commit()
        response={"id":order_to_update.id,
            "quantity": order_to_update.quantity,
            "pizza_size":order_to_update.pizza_size,
            "order_status":order_to_update.order_status}
        return jsonable_encoder(response)
    
@order_router.delete('/order/delete/{id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_an_order(id:int,Authrize:AuthJWT=Depends()):
    """ 
        ##  DELETE ORDER
        This route is used to delete an order by its ID.
        
    """
    try:
        Authrize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid Token ")
    order_to_delete=session.query(Order).filter(Order.id==id).first()
    session.delete(order_to_delete)
    session.commit()
    return order_to_delete
    
    