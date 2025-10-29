-- tables

CREATE TABLE IF NOT EXISTS Category (
	category_id serial PRIMARY KEY, 
	category_name varchar(120) UNIQUE NOT NULL);

CREATE TABLE IF NOT EXISTS Entreprise (
	entreprise_id varchar(256) PRIMARY KEY,
	entreprise_name varchar(256) NOT NULL,
  profileImageUrl varchar(256) DEFAULT NULL,
	mail varchar(150) DEFAULT NULL,
	phone varchar(50) DEFAULT NULL,
	web_site varchar(150),
	category_id integer REFERENCES Category (category_id));

CREATE TABLE IF NOT EXISTS Address (
	entreprise_id varchar(256) PRIMARY KEY REFERENCES Entreprise (entreprise_id),
	street varchar(256) DEFAULT NULL,
	zip_code varchar(50) DEFAULT NULL,
	city varchar(85) DEFAULT NULL,
	country varchar(56) DEFAULT NULL);

CREATE TABLE IF NOT EXISTS Rating (
	entreprise_id varchar(256) PRIMARY KEY REFERENCES Entreprise (entreprise_id),
	trustscore numeric NOT NULL,
	one_star integer NOT NULL,
	two_star integer NOT NULL,
	three_star integer NOT NULL,
	four_star integer NOT NULL,
	five_star integer NOT NULL);

-- vues

CREATE OR REPLACE VIEW public.all_company_raw_data
 AS
 SELECT entreprise.entreprise_id,
    entreprise.entreprise_name,
    entreprise.profileImageUrl,
    entreprise.mail,
    entreprise.phone,
    entreprise.web_site,
    address.street,
    address.zip_code,
    address.city,
    address.country,
    rating.one_star,
    rating.two_star,
    rating.three_star,
    rating.four_star,
    rating.five_star,
	rating.trustScore
   FROM entreprise,
    address,
    category,
    rating
  WHERE entreprise.entreprise_id::text = address.entreprise_id::text AND entreprise.category_id = category.category_id AND entreprise.entreprise_id::text = rating.entreprise_id::text;

CREATE OR REPLACE VIEW public.company_ratings
 AS
 SELECT entreprise_name,
    round((one_star_percent + 2 * two_star_percent + 3 * three_star_percent + 4 * four_star_percent + 5 * five_star_percent)::numeric / 120::numeric, 2) AS average_rating,
	trustScore,
    nb_reviews,
    one_star_percent,
    two_star_percent,
    three_star_percent,
    four_star_percent,
    five_star_percent
   FROM ( SELECT all_company_raw_data.entreprise_name,
            (all_company_raw_data.one_star::double precision / (all_company_raw_data.one_star + all_company_raw_data.two_star + all_company_raw_data.three_star + all_company_raw_data.four_star + all_company_raw_data.five_star)::double precision * 100::double precision)::integer AS one_star_percent,
            (all_company_raw_data.two_star::double precision / (all_company_raw_data.one_star + all_company_raw_data.two_star + all_company_raw_data.three_star + all_company_raw_data.four_star + all_company_raw_data.five_star)::double precision * 100::double precision)::integer AS two_star_percent,
            (all_company_raw_data.three_star::double precision / (all_company_raw_data.one_star + all_company_raw_data.two_star + all_company_raw_data.three_star + all_company_raw_data.four_star + all_company_raw_data.five_star)::double precision * 100::double precision)::integer AS three_star_percent,
            (all_company_raw_data.four_star::double precision / (all_company_raw_data.one_star + all_company_raw_data.two_star + all_company_raw_data.three_star + all_company_raw_data.four_star + all_company_raw_data.five_star)::double precision * 100::double precision)::integer AS four_star_percent,
            (all_company_raw_data.five_star::double precision / (all_company_raw_data.one_star + all_company_raw_data.two_star + all_company_raw_data.three_star + all_company_raw_data.four_star + all_company_raw_data.five_star)::double precision * 100::double precision)::integer AS five_star_percent,
            all_company_raw_data.one_star + all_company_raw_data.two_star + all_company_raw_data.three_star + all_company_raw_data.four_star + all_company_raw_data.five_star AS nb_reviews,
			all_company_raw_data.trustScore
           FROM all_company_raw_data) temp
  ORDER BY (round((one_star_percent + 2 * two_star_percent + 3 * three_star_percent + 4 * four_star_percent + 5 * five_star_percent)::numeric / 120::numeric, 2)) DESC;