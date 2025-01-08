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
from typing import Dict, List

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apis.open_v3.serializers.user import (
    TenantUserDepartmentListInputSLZ,
    TenantUserDepartmentListOutputSLZ,
    TenantUserDisplayNameListInputSLZ,
    TenantUserDisplayNameListOutputSLZ,
    TenantUserRetrieveOutputSLZ,
)
from bkuser.apps.data_source.models import (
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser

logger = logging.getLogger(__name__)


class TenantUserDisplayNameListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    批量根据用户 bk_username 获取用户展示名
    TODO: 性能较高，只查询所需字段，后续开发 DisplayName 支持表达式配置时添加 Cache 方案
    """

    pagination_class = None

    serializer_class = TenantUserDisplayNameListOutputSLZ

    def get_queryset(self):
        slz = TenantUserDisplayNameListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # TODO: 由于目前 DisplayName 渲染只与 full_name 相关，所以只查询 full_name
        # 后续支持表达式，则需要查询表达式可配置的所有字段
        return (
            TenantUser.objects.filter(id__in=data["bk_usernames"])
            .select_related("data_source_user")
            .only("id", "data_source_user__full_name")
        )

    @swagger_auto_schema(
        tags=["open_v3.user"],
        operation_id="batch_query_user_display_name",
        operation_description="批量查询用户展示名",
        query_serializer=TenantUserDisplayNameListInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserDisplayNameListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TenantUserRetrieveApi(OpenApiCommonMixin, generics.RetrieveAPIView):
    """
    根据用户 bk_username 获取用户信息
    """

    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    serializer_class = TenantUserRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["open_v3.user"],
        operation_id="retrieve_user",
        operation_description="查询用户信息",
        responses={status.HTTP_200_OK: TenantUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TenantUserDepartmentListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    根据用户 bk_username 获取用户所在部门列表信息（支持是否包括祖先部门）
    """

    pagination_class = None

    serializer_class = TenantUserDepartmentListOutputSLZ

    @swagger_auto_schema(
        tags=["open_v3.user"],
        operation_id="query_user_department",
        operation_description="查询用户所在部门列表",
        query_serializer=TenantUserDepartmentListInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserDepartmentListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        slz = TenantUserDepartmentListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_user = get_object_or_404(TenantUser.objects.all(), id=kwargs["id"])

        return Response(
            TenantUserDepartmentListOutputSLZ(self._get_dept_info(tenant_user, data["with_ancestors"]), many=True).data
        )

    def _get_dept_info(self, tenant_user: TenantUser, with_ancestors: bool) -> List[Dict]:
        """
        获取用户所在部门列表信息
        """
        # 根据 data_source_user 查询用户所属的数据源部门
        dept_user_relations = DataSourceDepartmentUserRelation.objects.filter(
            user=tenant_user.data_source_user
        ).select_related("department")

        # 如果该用户没有部门关系，则返回空列表
        if not dept_user_relations:
            return []

        # 根据数据源部门 ID 查询用户所属的租户部门
        tenant_departments = TenantDepartment.objects.filter(
            data_source_department_id__in=[relation.department_id for relation in dept_user_relations],
            tenant_id=tenant_user.tenant_id,
        ).select_related("data_source_department")

        dept_info_map = {}
        for dept in tenant_departments:
            # 获取租户部门的 ID 与对应的部门名称
            dept_info = {"id": dept.id, "name": dept.data_source_department.name}
            # 若 with_ancestors 为 True，则获取部门的祖先部门列表信息
            if with_ancestors:
                dept_info["ancestors"] = self._get_dept_ancestors(
                    dept.data_source_department_id, tenant_user.tenant_id
                )
            dept_info_map[dept.data_source_department_id] = dept_info

        return list(dept_info_map.values())

    @staticmethod
    def _get_dept_ancestors(dept_id: int, tenant_id: str) -> List[Dict]:
        """
        获取某个部门的祖先部门列表信息（包含租户部门 ID 与 部门名称）
        """
        relation = DataSourceDepartmentRelation.objects.filter(department_id=dept_id).first()
        # 若该部门不存在祖先节点，则返回空列表
        if not relation:
            return []
        # 返回的祖先部门默认以降序排列，从根祖先部门 -> 父部门
        ancestors = relation.get_ancestors().select_related("department")

        # 根据祖先数据源部门 ID 查询祖先租户部门
        ancestor_departments = TenantDepartment.objects.filter(
            data_source_department_id__in=[ancestor.department_id for ancestor in ancestors],
            tenant_id=tenant_id,
        ).select_related("data_source_department")

        return [
            # 获取祖先租户部门的 ID 与对应的部门名称
            {
                "id": ancestor_department.id,
                "name": ancestor_department.data_source_department.name,
            }
            for ancestor_department in ancestor_departments
        ]
