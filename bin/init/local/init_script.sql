/*init authorizations for role1*/
/*auth-hello : role1*/
insert into sm_api(name, url) values('auth-hello', '/hello/auth-hello/');
insert into sm_menu(name, code) values('menu1', '1');
insert into sm_menu_apis(smmenu_id, smapi_id) values((select id from sm_menu where name='menu1'), (select id from sm_api where name='auth-hello'));
insert into sm_role(name) values('role1');
insert into sm_role_menus(smrole_id, smmenu_id) values((select id from sm_role where name='role1'), (select id from sm_menu where name='menu1'));

/*auth-hello-2 : role1*/
insert into sm_api(name, url) values('auth-hello-2', '/hello/auth-hello-2/');
insert into sm_menu_apis(smmenu_id, smapi_id) values((select id from sm_menu where name='menu1'), (select id from sm_api where name='auth-hello-2'));
/* de-auth auth-hello-2*/
delete from sm_menu_apis where smmenu_id=(select id from sm_menu where name='menu1') and smapi_id=(select id from sm_api where name='auth-hello-2')
/* re-auth auth-hello-2*/
insert into sm_menu_apis(smmenu_id, smapi_id) values((select id from sm_menu where name='menu1'), (select id from sm_api where name='auth-hello-2'));


