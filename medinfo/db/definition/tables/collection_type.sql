CREATE TABLE IF NOT EXISTS collection_type
(
	collection_type_id INTEGER NOT NULL, -- SIGNED option for MySQL
	name VARCHAR(255) NOT NULL,
	description TEXT,
	CONSTRAINT collection_type_pkey PRIMARY KEY (collection_type_id),
	CONSTRAINT collection_type_key UNIQUE (name)
);
-- ALTER TABLE collection_type ADD CONSTRAINT collection_type_pkey PRIMARY KEY (collection_type_id);
-- ALTER TABLE collection_type ADD CONSTRAINT collection_type_key UNIQUE (name);

-- Insert base collection types expected
INSERT INTO collection_type (collection_type_id, name, description)
SELECT
	1, 'Recommendation', 'Recommendation Level - For example, 1=Generally agreed recommendation, 2=Moderate or conflicting support for recommendation, 2.1=Recommendation default without quantification, 2.5=Conflicting support, favor not recommending, or highly conditional, 3=Generally agreed against'
WHERE NOT EXISTS (
	SELECT * FROM collection_type WHERE collection_type_id = 1
);

INSERT INTO collection_type (collection_type_id, name, description)
SELECT
	2, 'Evidence', 'Evidence Level - For example, 1=(a) Strong evidence, 2=(b) Moderate evidence, 3=(c) Weak evidence'
WHERE NOT EXISTS (
	SELECT * FROM collection_type WHERE collection_type_id = 2
);

INSERT INTO collection_type (collection_type_id, name, description)
SELECT
	3, 'Reference','Reference Level - For example, 1=Explicitly referenced in collection, 2=Implied use in collection, 2.5=Consistent with properties of collection, but may be highly conditional or secondary choice, 3=Referenced *against* use'
WHERE NOT EXISTS (
	SELECT * FROM collection_type WHERE collection_type_id = 3
);

INSERT INTO collection_type (collection_type_id, name, description)
SELECT
		4, 'OrderSet', '1=Default-selected, 2=Available, 2.5=Available under sub-menu'
WHERE NOT EXISTS (
		SELECT * FROM collection_type WHERE collection_type_id = 4
);

INSERT INTO collection_type (collection_type_id, name, description)
SELECT
		5, 'DiagnosisLink', 'Link an (admission) diagnosis designated by clinical_item_id to the item collection (value = 3: reference guidelines or value = 4: order set collections).'
WHERE NOT EXISTS (
		SELECT * FROM collection_type WHERE collection_type_id = 5
);
