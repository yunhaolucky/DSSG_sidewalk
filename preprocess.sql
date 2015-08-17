-- STEP1: get a more clear dataset from raw_sidewalks
CREATE TABLE processed_sidewalks AS
SELECT id, ST_LineMerge(ST_Transform(geom,2926)) AS geom, segkey, curbramphighyn, curbramplowyn, curbrampmidyn from raw_sidewalks;
------ To check the output table, try this
SELECT * FROM processed_sidewalks limit 5;
------ Create spatial index and primary key
CREATE INDEX spatial_sidewalks ON processed_sidewalks USING gist(geom);
ALTER TABLE processed_sidewalks ADD PRIMARY KEY (id);

-- Remove all not valid geometries
UPDATE processed_sidewalks 
SET s_geom = null
WHERE GeometryType(geom) != 'LINESTRING';