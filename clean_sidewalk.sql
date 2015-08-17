CREATE TABLE nodes_for_cleaned (
s_id integer, 
g_id integer,
type varchar(2),
id serial
);
SELECT AddGeometryColumn ('public','nodes_for_cleaned','geom',2926,'POINT',2);

INSERT INTO nodes_for_cleaned(s_id, g_id,type, geom )
SELECT s.s_id, s.b_id, 'S', ST_StartPoint(s.s_geom) as geom 
FROM grouped_sidewalks as s;

INSERT INTO nodes_for_cleaned(s_id, g_id,type, geom )
SELECT s.s_id, s.b_id, 'E', ST_EndPoint(s.s_geom) as geom 
FROM grouped_sidewalks as s;

SELECT * FROM nodes_for_cleaned;




WITH RECURSIVE t(g_id) AS (
    VALUES (1)
  UNION ALL
    SELECT g_d+1 FROM t WHERE n < (SELECT max(b_id) from grouped_sidewalks)
)
SELECT * FROM t;


WITH RECURSIVE group_combine(g_id, s_id1, s_id2, s_geom1, s_geom2, cycle) AS (
        SELECT g_id, g.link, g.data, 1,
          ARRAY[g.id],
          false
        FROM (SELECT * FROM nodes_for_cleaned WHERE nodes_for_cleaned.g_id = 1)
        JOIN 
      UNION ALL
        SELECT g.id, g.link, g.data, sg.depth + 1,
          path || g.id,
          g.id = ANY(path)
        FROM graph g, search_graph sg
        WHERE g.id = sg.link AND NOT cycle
)
SELECT * FROM group_combine;


WITH RECURSIVE t(b_id) AS (
    SELECT s1.b_id, s1.s_id, s2.s_id  FROM (SELECT * FROM grouped_sidewalks WHERE b_id = 1) as s1 , (SELECT * FROM grouped_sidewalks WHERE b_id = 1) as s2
  UNION ALL
    SELECT s1.b_id+1,s1.s_id, s2.s_id FROM  t, grouped_sidewalks as s1 ,grouped_sidewalks as s2 WHERE s1.b_id = t.b_id + 1 AND s2.b_id  = t.b_id + 1
)
SELECT * FROM t;

