-- INSERT INTO dev_Files (id, yt_id, path) VALUES
-- (2, 'jGBp5HBLFs', '\songs\-jGBp5HBLFs.opus'), 
-- (3, '2lTB1pIg1y0', 'songs\2lTB1pIg1y0.opus');
-- Know that sql has built-in string literals. \ is used to escape characters

UPDATE dev_Files
SET id = 2, yt_id = '-jGBp5HBLFs', path = 'songs\-jGBp5HBLFs.opus'
WHERE id = 2;

UPDATE dev_Files
SET id = 3, yt_id = '2lTB1pIg1y0', path = 'songs\2lTB1pIg1y0.opus'
WHERE id =3;

UPDATE dev_Files
SET path = REPLACE(path, '\\', '\');


SELECT * FROM dev_Files WHERE true;