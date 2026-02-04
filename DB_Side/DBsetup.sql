create table testtable(
    id int primary key auto_increment,
    name varchar(50) unique
);

insert
  into testtable
values(DEFAULT, 'name1');

insert
  into testtable
values(DEFAULT, 'name2');

select *
  from testtable;