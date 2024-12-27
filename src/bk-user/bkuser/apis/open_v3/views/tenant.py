# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status

from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apis.open_v3.serializers.tenant import (
    TenantListOutputSLZ,
    TenantUserDisplayNameListInputSLZ,
    TenantUserDisplayNameListOutputSLZ,
)
from bkuser.apps.tenant.models import Tenant, TenantUser

logger = logging.getLogger(__name__)


class TenantListApi(OpenApiCommonMixin, generics.ListAPIView):
    serializer_class = TenantListOutputSLZ
    queryset = Tenant.objects.all()

    @swagger_auto_schema(
        tags=["open_v3.tenant"],
        operation_id="list_tenant",
        operation_description="获取租户列表",
        responses={status.HTTP_200_OK: TenantListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TenantUserDisplayNameListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    批量根据用户 bk_username 获取用户展示名
    Note：性能较高，只查询所需字段，后续开发 DisplayName 支持表达式配置时添加 Cache 方案
    """

    serializer_class = TenantUserDisplayNameListOutputSLZ

    pagination_class = None

    def get_queryset(self):
        slz = TenantUserDisplayNameListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_users = (
            TenantUser.objects.filter(id__in=data["bk_usernames"])
            .select_related("data_source_user")
            .only("id", "data_source_user__full_name")
        )

        # 可能存在部分用户的 bk_username 非法，无法查询到对应的 display_name
        if tenant_users.count() != len(data["bk_usernames"]):
            logger.info("%d users' display_name not found", len(data["bk_usernames"]) - tenant_users.count())

        return tenant_users

    @swagger_auto_schema(
        tags=["open_v3.tenant"],
        operation_id="list_display_name",
        operation_description="批量获取用户展示名",
        responses={status.HTTP_200_OK: TenantUserDisplayNameListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
