from fastapi import FastAPI, Depends

from src.RetailCRM.middleware import HttpxExceptionMiddleware
from src.RetailCRM.schemas import GetClientsWithParams, CreateClient, GetClientOrdersWithParams, Order, OrderPayment
from src.RetailCRM.use_cases import UserUseCases
from src.RetailCRM.utils import get_clients_params, get_order_list_params

app = FastAPI()
app.add_middleware(HttpxExceptionMiddleware)


@app.get("/get_client_list")
async def get_client_list(
        data: GetClientsWithParams = Depends(get_clients_params)
):
    us = UserUseCases()
    return await us.get_clients_list(data)


@app.post("/create_client")
async def create_client(
        data: CreateClient
):
    us = UserUseCases()
    return await us.create_client(data)


@app.get("/get_order_list")
async def get_order_list(
        data: GetClientOrdersWithParams = Depends(get_order_list_params)
):
    us = UserUseCases()
    return await us.get_client_orders(data)


@app.post("/make_order")
async def make_order(
        data: Order
):
    us = UserUseCases()
    return await us.make_order(data)


@app.post("/make_payment")
async def make_payment(
        data: OrderPayment
):
    us = UserUseCases()
    return await us.make_payment(data)
