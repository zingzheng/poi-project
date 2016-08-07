create table JobInfo (
  id integer primary key autoincrement,
  core_type text not null,
  map_type text not null,
  region_type text not null,
  region text not null,
  keyword text not null,
  owner text not null,
  createTime text not null,
  finishTime text not null,
  status text not null
);