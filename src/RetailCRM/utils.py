from typing import Optional

import httpx
from fastapi import Query

from src.RetailCRM.schemas import GetClientOrdersWithParams, GetClientsWithParams
from src.config import settings

from enum import Enum


class RequestTypes(Enum):
    GET = "GET"
    POST = "POST"


def get_clients_params(
        name: Optional[str] = Query(None, description="Имя"),
        email: Optional[str] = Query(None, description="Email"),
        date_from: Optional[str] = Query(None, description="Дата создания от"),
        date_to: Optional[str] = Query(None, description="Дата создания до"),
        limit: Optional[int] = Query(100, description="Лимит записей"),
        page: Optional[int] = Query(1, description="Страница")
) -> GetClientsWithParams:
    return GetClientsWithParams(
        name=name,
        email=email,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        page=page
    )


def get_order_list_params(
        customer_id: Optional[int] = Query(None, description="ID клиента"),
        limit: Optional[int] = Query(100, description="Лимит записей"),
        page: Optional[int] = Query(1, description="Страница")
) -> GetClientOrdersWithParams:
    return GetClientOrdersWithParams(
        customer_id=customer_id,
        limit=limit,
        page=page
    )


def _get_headers() -> dict:
    headers = {
        "X-API-KEY": settings.SECRET_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    return headers


async def httpx_request(url: str, headers: dict | None = None, params: dict | None = None, data: str | None = None,
                        request_type: Enum | None = RequestTypes.GET) -> any:
    if headers is None:
        headers = _get_headers()
    async with httpx.AsyncClient() as client:
        response = await client.request(
            url=url,
            method=request_type.value,
            headers=headers,
            params=params,
            data=data
        )
        if response.status_code >= 400:
            raise httpx.HTTPStatusError(
                message=f"HTTP error {response.status_code}",
                request=response.request,
                response=response
            )
        return response.json()
