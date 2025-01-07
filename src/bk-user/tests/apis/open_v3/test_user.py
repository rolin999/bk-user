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
import pytest
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from django.conf import settings
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserDisplayNameList:
    def test_standard(self, api_client):
        zhangsan_id = TenantUser.objects.get(data_source_user__code="zhangsan").id
        lisi_id = TenantUser.objects.get(data_source_user__code="lisi").id
        resp = api_client.get(
            reverse("open_v3.tenant_user.display_name.list"), data={"bk_usernames": ",".join([zhangsan_id, lisi_id])}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan_id, lisi_id}
        assert {t["display_name"] for t in resp.data} == {"张三", "李四"}

    def test_with_invalid_bk_usernames(self, api_client):
        zhangsan_id = TenantUser.objects.get(data_source_user__code="zhangsan").id
        resp = api_client.get(
            reverse("open_v3.tenant_user.display_name.list"), data={"bk_usernames": ",".join([zhangsan_id, "invalid"])}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == zhangsan_id
        assert resp.data[0]["display_name"] == "张三"

    def test_with_no_bk_usernames(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.display_name.list"), data={"bk_usernames": ""})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_with_invalid_length(self, api_client):
        resp = api_client.get(
            reverse("open_v3.tenant_user.display_name.list"),
            data={
                "bk_usernames": ",".join(
                    map(str, range(1, settings.BATCH_QUERY_USER_DISPLAY_NAME_BY_BK_USERNAME_LIMIT + 2))
                )
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserRetrieveApi:
    def test_standard(self, api_client, random_tenant):
        zhangsan = TenantUser.objects.get(data_source_user__code="zhangsan")
        resp = api_client.get(reverse("open_v3.tenant_user.retrieve", kwargs={"id": zhangsan.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["bk_username"] == zhangsan.id
        assert resp.data["display_name"] == "张三"
        assert resp.data["language"] == "zh-cn"
        assert resp.data["time_zone"] == "Asia/Shanghai"
        assert resp.data["tenant_id"] == random_tenant.id

    def test_tenant_not_found(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.retrieve", kwargs={"id": "not_exist"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserDepartmentList:
    def test_with_no_ancestors(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__code="zhangsan")
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        resp = api_client.get(reverse("open_v3.tenant_user.department.list", kwargs={"id": zhangsan.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data[0]["id"] == company.id
        assert resp.data[0]["name"] == "公司"

    def test_with_ancestors(self, api_client):
        lisi = TenantUser.objects.get(data_source_user__code="lisi")
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        dept_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")
        resp = api_client.get(
            reverse("open_v3.tenant_user.department.list", kwargs={"id": lisi.id}), data={"with_ancestors": True}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {d["id"] for d in resp.data} == {dept_a.id, dept_aa.id}
        assert {d["name"] for d in resp.data} == {"部门A", "中心AA"}
        assert resp.data[0]["ancestors"] == [{"id": company.id, "name": "公司"}]
        assert resp.data[1]["ancestors"] == [{"id": company.id, "name": "公司"}, {"id": dept_a.id, "name": "部门A"}]

    def test_with_invalid_id(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.department.list", kwargs={"id": "a1e5b2f6c3g7d4h8"}))
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_with_no_department(self, api_client):
        freedom = TenantUser.objects.get(data_source_user__code="freedom")
        resp = api_client.get(
            reverse("open_v3.tenant_user.department.list", kwargs={"id": freedom.id}), data={"with_ancestors": True}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0
