from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.domain.platform_role_status import PlatformRoleStatus
from app.domain.platform_user_status import PlatformUserStatus
from app.services.platform_runtime_authorization_service import (
    PlatformRuntimeAuthorizationService,
)

ORG="org-42"
USER="user-42"
PERM="platform-administration.manage"
NOW=datetime(2026,8,13,12,0,tzinfo=UTC)

def user(**kw):
    d=dict(id=USER,organization_id=ORG,status=PlatformUserStatus.ACTIVE.value,is_active=True,created_via_bootstrap=False); d.update(kw); return SimpleNamespace(**d)

def assignment(**kw):
    d=dict(id="a1",organization_id=ORG,platform_user_id=USER,platform_role_id="r1",assigned_at=NOW-timedelta(days=1),expires_at=None,is_active=True); d.update(kw); return SimpleNamespace(**d)

def role(**kw):
    d=dict(id="r1",organization_id=ORG,role_key="platform-administrator",status=PlatformRoleStatus.ACTIVE.value,is_active=True); d.update(kw); return SimpleNamespace(**d)

def permission(**kw):
    d=dict(id="p1",permission_key=PERM,is_active=True); d.update(kw); return SimpleNamespace(**d)

def mapping(**kw):
    d=dict(id="m1",organization_id=ORG,platform_role_id="r1",platform_permission_id="p1",is_active=True); d.update(kw); return SimpleNamespace(**d)

def build(u=None, assignments=None, roles=None, perm=None, mappings=None):
    db=MagicMock(); ur=MagicMock(); ar=MagicMock(); rr=MagicMock(); mr=MagicMock(); pr=MagicMock()
    ur.get_by_id.return_value=user() if u is None else u
    ar.list_for_user.return_value=[assignment()] if assignments is None else assignments
    role_records=[role()] if roles is None else roles
    rr.get_by_id.side_effect=lambda rid: next((x for x in role_records if x.id==rid),None)
    pr.get_by_key.return_value=permission() if perm is None else perm
    map_records=[mapping()] if mappings is None else mappings
    mr.list_for_role.side_effect=lambda organization_id,platform_role_id:[x for x in map_records if x.organization_id==organization_id and x.platform_role_id==platform_role_id]
    svc=PlatformRuntimeAuthorizationService(db,platform_user_repository=ur,platform_role_assignment_repository=ar,platform_role_repository=rr,platform_role_permission_repository=mr,platform_permission_repository=pr)
    return svc,ar

def evaluate(svc):
    return svc.evaluate(organization_id=ORG,platform_user_id=USER,permission_key=PERM,now=NOW)

def test_allow_active_chain():
    assert evaluate(build()[0]).allowed is True

def test_foreign_user_denied():
    svc,ar=build(u=user(organization_id="org-92")); r=evaluate(svc)
    assert not r.allowed and r.reason=="PlatformUserNotFoundInOrganization"; ar.list_for_user.assert_not_called()

def test_invited_user_denied():
    svc,ar=build(u=user(status=PlatformUserStatus.INVITED.value)); r=evaluate(svc)
    assert not r.allowed and r.reason=="PlatformUserNotActive"; ar.list_for_user.assert_not_called()

def test_expired_assignment_denied():
    svc,_=build(assignments=[assignment(expires_at=NOW-timedelta(seconds=1))])
    assert evaluate(svc).allowed is False

def test_future_assignment_denied():
    svc,_=build(assignments=[assignment(assigned_at=NOW+timedelta(minutes=1))])
    assert evaluate(svc).allowed is False

def test_disabled_role_denied():
    svc,_=build(roles=[role(status=PlatformRoleStatus.DISABLED.value)])
    assert evaluate(svc).allowed is False

def test_foreign_role_denied():
    svc,_=build(roles=[role(organization_id="org-92")])
    assert evaluate(svc).allowed is False

def test_unknown_permission_denied():
    svc,ar=build(perm=False); svc.permission_repository.get_by_key.return_value=None
    r=evaluate(svc); assert not r.allowed and r.reason=="PermissionNotDefined"; ar.list_for_user.assert_not_called()

def test_missing_mapping_denied():
    svc,_=build(mappings=[]); assert evaluate(svc).allowed is False

def test_bootstrap_is_not_bypass():
    svc,_=build(u=user(created_via_bootstrap=True),assignments=[])
    assert evaluate(svc).allowed is False
