-- init admin user:

create database brighterpage;

grant select, insert, delete, update on brighterpage.* to 'www-data'@'localhost' identified by 'www-data';

insert into users(_id, name, role, email, verified, binds, passwd, image_url, locked_time, creation_time, modified_time, version) values('001383729881018b677b2776c24451e9b5f30a03ea5d73c000', 'Admin', 0, 'admin@brighterpage.com', 0, '', '50d6ac79c0237ef7be80f58f90fe8fbd', '/static/img/user.png', 0.0, 1383729899.450415, 1383729899.450415, 0);
