from models import database_beanie
from fastapi import Request
from typing import Optional
from bson import ObjectId
from models import base_aggregation
from fastapi_pagination import Params, Page
from fastapi_pagination.ext.beanie import paginate


class MongoAggregation:

    def __init__(self, request: Request):
        self.request = request
        self.is_superuser: bool = request.is_superuser
        self.filter: Optional[dict] = request.client_model.filter
        self.project: Optional[dict] = request.client_model.project
        self.sort: str = request.client_model.sort
        self.skip: int = request.client_model.skip
        self.limit: int = request.client_model.limit
        self.params: Params = request.paginator

    def __config(self, base: list):
        if self.filter:
            base.append({"$match": self.filter})
        if self.project:
            base.append({"$project": self.project})
        base.append({"$sort": {"_id": 1 if self.sort == "asc" else -1}})
        base.append({"$limit": self.limit})
        base.append({"$skip": self.skip})
        base.append({"$unset": "_id"})
        return base

    def clear_query_response(self, response: Page):

        return {"items": response.items, "page": response.page, "pages": response.pages, "size": response.size, "total": response.total}

    async def user_info(self):
        if not self.is_superuser:
            user_id: str = self.request.user_id
            self.filter = {"_id": ObjectId(user_id)}
        response = await paginate(
            query=database_beanie.User.aggregate(
                self.__config(base_aggregation.user_info())
            ),
            params=self.params
        )
        if not response:
            return None 
        return self.clear_query_response(response)
