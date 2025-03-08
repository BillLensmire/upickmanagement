BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "plants_plant" (
	"id"	integer NOT NULL,
	"name"	varchar(100) NOT NULL,
	"description"	text NOT NULL,
	"research_notes"	text,
	"seed_type"	varchar(20) NOT NULL,
	"planting_method"	varchar(20) NOT NULL,
	"spacing_between_plants"	integer NOT NULL,
	"spacing_between_rows"	integer NOT NULL,
	"germination_temp_min"	integer,
	"germination_temp_max"	integer,
	"days_to_germinate"	integer,
	"days_to_maturity"	integer,
	"days_from_seed_to_transplant"	integer,
	"days_from_frost_to_transplant"	integer,
	"height_inches"	integer NOT NULL,
	"is_perennial"	bool NOT NULL,
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	"group_id"	integer,
	FOREIGN KEY("group_id") REFERENCES "auth_group"("id") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "plants_plant_companion_plants" (
	"id"	integer NOT NULL,
	"from_plant_id"	bigint NOT NULL,
	"to_plant_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("to_plant_id") REFERENCES "plants_plant"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("from_plant_id") REFERENCES "plants_plant"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "plants_variety" (
	"id"	integer NOT NULL,
	"variety_name"	varchar(100) NOT NULL,
	"scientific_name"	varchar(100) NOT NULL,
	"variety_description"	text NOT NULL,
	"variety_planting_method"	varchar(20) NOT NULL,
	"variety_spacing_between_plants"	integer,
	"variety_spacing_between_rows"	integer,
	"variety_days_to_maturity"	integer,
	"variety_days_from_seed_to_transplant"	integer,
	"variety_days_from_frost_to_transplant"	integer,
	"variety_planting_season"	varchar(20) NOT NULL,
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	"group_id"	integer,
	"variety_plant_id"	bigint,
	FOREIGN KEY("group_id") REFERENCES "auth_group"("id") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("variety_plant_id") REFERENCES "plants_plant"("id") DEFERRABLE INITIALLY DEFERRED
);
INSERT INTO "plants_plant" ("id","name","description","research_notes","seed_type","planting_method","spacing_between_plants","spacing_between_rows","germination_temp_min","germination_temp_max","days_to_germinate","days_to_maturity","days_from_seed_to_transplant","days_from_frost_to_transplant","height_inches","is_perennial","created_at","updated_at","group_id") VALUES (3,'Beet','','','VEGETABLE','DIRECT',3,12,70,75,7,50,35,-14,8,0,'2025-02-27 21:08:10.238380','2025-02-27 21:08:10.238391',1),
 (4,'Carrot','','','VEGETABLE','DIRECT',2,18,70,75,10,56,0,-21,12,0,'2025-02-28 22:10:00.480242','2025-02-28 22:10:00.480251',1),
 (9,'Cucumber','','Cucumber and summer squash seeds should germinate in 3 to 5 days at soil temperatures of 70-85'' F.  Four or five seeds are commonly planted in each container. After germination, thin to leave the strongest two seedlings. It is generally best to thin by pinching off or cutting the stems with a knife, as pulling can result in injury to the roots of the remaining seedlings.','VEGETABLE','TRANSPLANT',12,36,70,85,10,60,21,7,36,0,'2025-02-28 20:40:09.920239','2025-02-28 20:40:09.920262',1),
 (10,'Cantaloupe','','The practical soil temperature for germinating most melon seeds is 80°-90° F., although the acceptable range is from a low of 70° to a high of 95° F. If possible, use thermostatically controlled electric heating cables to maintain the desired soil temperatures.

A general recommendation is to plant three to five seeds in each container, and thin to the two best plants after the seedlings emerge.','VEGETABLE','TRANSPLANT',18,60,70,80,7,76,21,14,12,0,'2025-02-28 22:09:31.768188','2025-02-28 22:09:31.768210',1),
 (13,'Onion - Sets','','','VEGETABLE','DIRECT',4,18,0,0,0,100,0,-28,12,0,'2025-02-28 22:13:28.725887','2025-02-28 22:13:28.725897',1),
 (16,'Pepper - Hot','','','VEGETABLE','TRANSPLANT',18,24,80,82,14,70,42,7,24,0,'2025-02-28 22:14:09.918862','2025-02-28 22:14:09.918872',1),
 (19,'Pepper - Bell','','Pepper seed germinates rather slowly, requiring 8 days at a soil temperature of 75°-80° F. Following
germination, lower the soil temperature to 65°-68° F. to produce stocky plants. Pepper seedlings should
be ready for transplanting (when the first true leaf is visible) to other containers 15 to 20 days after the
seed is sown. Peppers require growing conditions similar to those for tomatoes.','VEGETABLE','TRANSPLANT',18,24,65,80,14,70,42,7,24,0,'2025-02-28 22:14:01.645611','2025-02-28 22:14:01.645621',1),
 (21,'Squash - Summer','','Cucumber and summer squash seeds should germinate in 3 to 5 days at soil temperatures of 70-85'' F.  Four or five seeds are commonly planted in each container. After germination, thin to leave the strongest two seedlings. It is generally best to thin by pinching off or cutting the stems with a knife, as pulling can result in injury to the roots of the remaining seedlings.','VEGETABLE','TRANSPLANT',24,36,80,83,7,35,21,14,18,0,'2025-02-28 20:27:11.247908','2025-02-28 20:27:11.247915',1),
 (25,'Squash - Winter','','','VEGETABLE','TRANSPLANT',36,36,80,83,7,90,21,14,18,0,'2025-02-20 21:09:19.415663','2025-02-20 21:09:34.852227',1),
 (31,'Tomato','','Tomato seeds germinate readily at a soil temperature of about 75° F. After the seedlings appear above ground, maintain soil temperatures as closely as possible to a range of 62°-65° F. with adequate light and moderate watering to produce stocky plants. The seedlings will be ready for removal from the seed flats 10 to 14 days after the seed is sown.

Tomato transplants that are 4 to 7 weeks old have the best potential for both earliest and greatest production.

Transplants of early-maturing determinate varieties such as Pik Red should be 4 to 5 weeks old, and some greenhouse varieties, such as jumbo, should be 6 to 8 weeks of age. Plants that are properly aged can be held a week in good condition if adverse weather delays planting.

Topping the plants prior to field setting, to promote branching, has not been found to be beneficial and may reduce early production.','VEGETABLE','TRANSPLANT',48,36,60,75,14,70,35,7,60,0,'2025-02-28 20:41:41.907572','2025-02-28 20:41:41.907583',1),
 (38,'Celeriac','','','VEGETABLE','TRANSPLANT',6,24,70,73,21,100,70,7,18,0,'2025-02-28 22:10:22.386771','2025-02-28 22:10:22.386782',1),
 (40,'Corn - Pop','','','VEGETABLE','DIRECT',12,36,65,65,6,100,0,7,60,0,'2025-02-28 22:10:58.537524','2025-02-28 22:10:58.537535',1),
 (43,'Corn - Sweet','','','VEGETABLE','DIRECT',12,36,65,65,6,100,0,7,60,0,'2025-02-28 22:11:09.527096','2025-02-28 22:11:09.527106',1),
 (44,'Brussel Sprouts','','','VEGETABLE','TRANSPLANT',24,36,70,80,7,118,35,-14,48,0,'2025-02-28 22:08:50.405718','2025-02-28 22:08:50.405727',1),
 (45,'Ground Cherry','','','VEGETABLE','TRANSPLANT',24,24,85,87,30,80,49,7,18,0,'2025-02-20 21:22:52.003802','2025-02-20 21:22:52.003872',1),
 (48,'Zinna','','','FLOWER','TRANSPLANT',9,12,73,75,6,75,28,7,18,0,'2025-02-20 22:04:13.709923','2025-02-25 19:51:37.151118',1),
 (52,'Sunflower - Single Stem','','','FLOWER','TRANSPLANT',6,12,73,75,10,60,14,7,60,0,'2025-02-20 22:06:14.636709','2025-02-25 19:50:39.821193',1),
 (54,'Sunflower - Branching','','','FLOWER','TRANSPLANT',24,12,73,75,10,60,14,7,60,0,'2025-02-20 22:07:19.487032','2025-02-25 19:50:28.377363',1),
 (55,'Marigold','','','FLOWER','TRANSPLANT',12,12,75,76,7,60,35,7,60,0,'2025-02-20 22:08:32.410018','2025-02-25 19:49:57.648468',1),
 (56,'Centaruea (Bachelor''s Button)','','','FLOWER','TRANSPLANT',9,12,65,67,10,90,21,0,18,0,'2025-02-20 22:09:41.633376','2025-02-25 19:49:27.736164',1),
 (57,'Gomphrena (Globe Amaranth)','','','FLOWER','TRANSPLANT',9,12,75,77,10,90,49,0,18,0,'2025-02-20 22:10:35.994909','2025-02-25 19:49:43.089978',1),
 (58,'Red Clover','','','VEGETABLE','DIRECT',0,0,70,80,20,0,0,-30,12,0,'2025-02-28 20:41:25.404273','2025-02-28 20:41:25.404281',1),
 (59,'Green Farm Mix','','','COVER_CROP','DIRECT',0,0,0,0,10,0,0,0,12,0,'2025-02-25 01:07:00.484383','2025-02-25 01:07:00.484446',1),
 (61,'Yellow raspberry','','','PERENNIAL','TRANSPLANT',36,60,70,70,0,0,0,0,49,1,'2025-02-25 17:36:19.193754','2025-02-25 19:49:15.999909',1),
 (63,'Sweet Potato','','Bed sweet potato roots in clean sand. Cover the roots with 3 to 4 additional inches of clean sand. Keep the roots moist and the temperature between 75°-85° F. during sprout growth.

Numerous sprouts will grow from a single potato root. These may be prepared for individual planting by pulling when sprouts are about 4 inches high. Rooted sprouts will easily separate from the planted potato roots.

About 1,000 rooted sprouts or slips can be produced from a bushel of potato roots at a single pulling.  When roots are left in the sand, additional plants will grow for later pullings. About 15 square feet are required to bed one bushel of roots, planted roughly 6 inches apart.','VEGETABLE','TRANSPLANT',18,36,NULL,NULL,NULL,NULL,NULL,NULL,10,0,'2025-02-28 20:16:11.378893','2025-02-28 20:16:11.378903',1),
 (64,'Onion','','','VEGETABLE','TRANSPLANT',4,18,60,70,10,110,56,0,12,0,'2025-02-28 22:12:50.055385','2025-02-28 22:12:50.055395',1),
 (65,'Apple Tree','Order Date: 8/19/2024
Approx Ship Date: 4/21/2025
7 x Enterprise(Co-op 30) - EMLA 7
7 x Liberty - EMLA 7
7 x Northern Spy - EMLA 7
7 x Crimson® Gala(Waliser) - G-969
7 x CrimsonCrisp® PP#16622 - G-969
7 x GoldRush(Co-op 38 Cltv) - G-890
7 x Nittany - G-890','The traditional goal the first season is a 5-gallon bucket per tree per week. If it rains, you can take a break. Irrigation is easier for a trellised G-890 orchard. You can drip irrigate long straight lines of closely spaced trees. We used two lines of drip tape per trellis for the first three years, laid right on the ground.
Eventually of course, these deteriorate; they can be replaced easily, but we are now looking to put thicker-walled orchard drip hose up off the ground, hung from the trellis. For the M-111 orchard, someone will need to spend a couple hours per week driving a water tank around and watering trees.

Weed control is especially important during the first three years of the orchard, and still pretty much a pressing issue in the G-890 orchard throughout its lifespan. The holy grail is a good well-rotted, hardwood wood chip mulch; we strive and aspire … but … does anyone have time for that?

Instead, landscape fabric has been our friend. In the G-890 orchard, we staple 3’ of fabric on either side of the trellis, leaving an approximately 1’ wide uncovered span in the middle where amendments, compost, and drip tape can go and where we try to keep up with weeds. We have also experimented with a Dutch white clover cover crop in this middle strip and seen some positive results. We do find that even when weeds get out of control in the uncovered span, trees seem to do just fine. The majority of their feeder roots are tucked underneath that 6’ span of moist, soft landscape fabric covered soil.

In the M-111 orchard, we stapled 4’x4’ squares of landscape fabric with a slit in the middle (these are commercially available pre-cut). These provided the young trees with a competitive edge during the first three years. We removed them after Year 3 and planted clover and some experimental comfrey as ground covers in the open space. By this point, the feeder roots on these robust rootstocks were out 5’ or 6’ in any direction and deep anchoring roots provided further nutrient- and water-mining power.
================================

We have narrowed our spray program to primarily just two OMRI-listed materials that many market growers will already be familiar with: Surround kaolin clay (for plum curculio and codling moth) and DiPel Bt (for codling moth). We tank mix some liquid fish fertilizer with each application. We are at a point where three to five well-timed sprays can get us through a season with reasonably pest-free apples.  

These sprays run from petal-fall to within a few weeks of harvest. When time and weather allow, we also do one to two dormant sprays of JMS stylet-oil in the fall and winter as an egg/larvae smotherer.  

Kaolin clay is a difficult material to spray. Initially we did the whole orchard with a motorized backpack sprayer but this was brutal on the body. So we purchased a three-point, PTO-driven mist sprayer. We quickly found out that Surround loves to clog TeeJet mist sprayers, no fun. The solution that has been working really well for us over the last three years is a spray gun plumbed into the mist sprayer pressurized system. We have an old, used gun, and it works great. We might splurge for a new John Bean 785 this year ($665). Sit on your tractor, drive along at ~1.5 mph, and lay the Surround on thick. When things go well, it looks like it snowed in the orchard afterward. Any old mist sprayer that makes pressure is gonna work with a decent spray gun. Having an agitator in the sprayer is another bonus, to help keep that clay in suspension.','FRUIT TREE','TRANSPLANT',180,240,0,0,0,0,0,0,120,1,'2025-03-02 00:21:32.355956','2025-03-02 00:21:32.355962',1),
 (66,'Asparagus','','','VEGETABLE','TRANSPLANT',12,48,NULL,NULL,NULL,NULL,NULL,NULL,36,1,'2025-02-28 22:07:54.318110','2025-02-28 22:07:54.318117',1),
 (67,'Garlic','','','VEGETABLE','DIRECT',6,12,NULL,NULL,NULL,NULL,NULL,NULL,18,0,'2025-02-28 22:12:14.562161','2025-02-28 22:12:14.562168',1),
 (68,'Rhubarb','','','VEGETABLE','TRANSPLANT',36,48,NULL,NULL,NULL,NULL,NULL,NULL,18,1,'2025-02-28 22:16:48.544176','2025-02-28 22:16:48.544206',1),
 (69,'Potato','','','VEGETABLE','DIRECT',12,36,NULL,NULL,NULL,NULL,NULL,NULL,36,0,'2025-02-28 22:20:18.094217','2025-02-28 22:20:18.094224',1);
INSERT INTO "plants_variety" ("id","variety_name","scientific_name","variety_description","variety_planting_method","variety_spacing_between_plants","variety_spacing_between_rows","variety_days_to_maturity","variety_days_from_seed_to_transplant","variety_days_from_frost_to_transplant","variety_planting_season","created_at","updated_at","group_id","variety_plant_id") VALUES (1,'red ace','','','DIRECT',3,12,50,35,-14,'SPRING','2025-02-27 20:44:20.153765','2025-02-27 20:44:20.153773',1,3),
 (2,'Merlin','','','DIRECT',3,12,50,35,-14,'SPRING','2025-02-27 21:26:09.287954','2025-02-27 21:26:09.287962',1,3),
 (3,'Darkmar 21','','asdfg asf f','TRANSPLANT',36,36,118,35,-14,'SPRING','2025-02-28 20:32:50.725032','2025-02-28 20:32:50.725052',1,44),
 (4,'Lensmire','','','TRANSPLANT',24,36,76,21,14,'SPRING','2025-02-28 20:36:47.945800','2025-02-28 20:36:47.945807',1,10),
 (5,'Yaya','','','DIRECT',2,12,56,0,-21,'SPRING','2025-02-27 21:27:38.146504','2025-02-27 21:27:38.146538',1,4),
 (6,'Mars','','','TRANSPLANT',10,18,100,70,7,'SPRING','2025-02-27 21:27:53.035514','2025-02-27 21:27:53.035547',1,38),
 (7,'Choice Mix','','','TRANSPLANT',9,12,90,21,0,'SPRING','2025-02-27 21:28:16.133252','2025-02-27 21:28:16.133286',1,56),
 (8,'Lensmire','','','DIRECT',8,24,100,0,7,'SPRING','2025-02-27 21:28:51.771985','2025-02-27 21:28:51.772019',1,40),
 (9,'Candy Astronomy Sweet Corn Landrace','','','DIRECT',8,24,100,0,7,'SPRING','2025-02-27 21:29:33.690954','2025-02-27 21:29:33.691021',1,40),
 (10,'Candy Mountain Sweet Corn','','','DIRECT',8,24,100,0,7,'SPRING','2025-02-27 21:29:44.214753','2025-02-27 21:29:44.214788',1,40),
 (11,'Diva','','','TRANSPLANT',12,36,60,21,7,'SPRING','2025-02-28 20:36:10.253399','2025-02-28 20:36:10.253411',1,9),
 (12,'Tanja','','','TRANSPLANT',12,36,60,21,7,'SPRING','2025-02-28 20:36:17.152177','2025-02-28 20:36:17.152188',1,9),
 (13,'Tendergreen Burpless','','','TRANSPLANT',12,36,60,21,7,'SPRING','2025-02-28 20:36:22.635127','2025-02-28 20:36:22.635148',1,9),
 (14,'QIS Formula Mix','','','TRANSPLANT',9,12,90,49,0,'SPRING','2025-02-27 21:31:00.541443','2025-02-27 21:31:00.541477',1,57),
 (15,'Aunt Molly''s','','','TRANSPLANT',24,24,80,49,7,'SPRING','2025-02-27 21:31:20.582517','2025-02-27 21:31:20.582556',1,45),
 (16,'Queen Sophia','','','TRANSPLANT',12,12,60,35,7,'SPRING','2025-02-27 21:31:46.976430','2025-02-27 21:31:46.976469',1,55),
 (17,'Red Baron','','','DIRECT',4,12,100,0,-28,'SPRING','2025-02-27 21:32:04.785047','2025-02-27 21:32:04.785082',1,13),
 (18,'Stuttgarter','','','DIRECT',4,12,100,0,-28,'SPRING','2025-02-27 21:32:17.034869','2025-02-27 21:32:17.034903',1,13),
 (19,'Sweet Globe','','','DIRECT',4,12,100,0,-28,'SPRING','2025-02-27 21:32:25.544300','2025-02-27 21:32:25.544334',1,13),
 (20,'Purple Beauty (large)','','','TRANSPLANT',24,24,70,42,7,'SPRING','2025-02-28 20:05:21.719085','2025-02-28 20:05:21.719092',1,19),
 (21,'King of the North (large)','','','TRANSPLANT',24,24,70,42,7,'SPRING','2025-02-28 20:05:05.759664','2025-02-28 20:05:05.759672',1,19),
 (22,'Golden Calwonder (large)','','','TRANSPLANT',24,24,70,42,7,'SPRING','2025-02-28 20:04:53.037191','2025-02-28 20:04:53.037199',1,19),
 (23,'Lensmire Red (large)','','','TRANSPLANT',24,24,70,42,7,'SPRING','2025-02-28 20:05:14.692953','2025-02-28 20:05:14.692961',1,19),
 (28,'Lensmire Poblano','','','TRANSPLANT',18,24,70,42,7,'SPRING','2025-02-27 21:34:07.658493','2025-02-27 21:34:07.658528',1,16),
 (29,'Mutabile','','','TRANSPLANT',24,36,35,21,14,'SPRING','2025-02-27 21:34:29.232681','2025-02-27 21:34:29.232714',1,21),
 (30,'Goldini 2','','','TRANSPLANT',24,36,35,21,14,'SPRING','2025-02-27 21:34:36.494245','2025-02-27 21:34:36.494285',1,21),
 (31,'Candystick Delicata','','Delicata','TRANSPLANT',36,36,90,21,14,'SPRING','2025-02-27 21:35:16.177394','2025-02-27 21:35:16.177413',1,25),
 (32,'Sonca Orange Butternut','','','TRANSPLANT',36,36,90,21,14,'SPRING','2025-02-27 21:35:07.096914','2025-02-27 21:35:07.096949',1,25),
 (33,'Little Gem Red Kuri','','','TRANSPLANT',36,36,90,21,14,'SPRING','2025-02-27 21:35:31.379401','2025-02-27 21:35:31.379447',1,25),
 (34,'Butternut Early Remix','','','TRANSPLANT',36,36,90,21,14,'SPRING','2025-02-27 21:35:44.849060','2025-02-27 21:35:44.849093',1,25),
 (35,'Daydream Mixture','','','TRANSPLANT',24,12,60,14,7,'SPRING','2025-02-27 21:36:07.779296','2025-02-27 21:36:07.779335',1,54),
 (36,'Summer Breeze Mix','','','TRANSPLANT',24,12,60,14,7,'SPRING','2025-02-27 21:36:16.417687','2025-02-27 21:36:16.417721',1,54),
 (37,'ProCut Red','','','TRANSPLANT',6,12,60,14,7,'SPRING','2025-02-27 21:36:32.259141','2025-02-27 21:36:32.259195',1,52),
 (38,'ProCut Red/Lemon','','','TRANSPLANT',6,12,60,14,7,'SPRING','2025-02-27 21:36:40.784666','2025-02-27 21:36:40.784700',1,52),
 (39,'ProCut Plum','','','TRANSPLANT',6,12,60,14,7,'SPRING','2025-02-27 21:36:48.307690','2025-02-27 21:36:48.307727',1,52),
 (40,'ProCut Orange Excel','','','TRANSPLANT',6,12,60,14,7,'SPRING','2025-02-27 21:37:06.898065','2025-02-27 21:37:06.898102',1,52),
 (41,'42 Day (D) (cherry)','','','TRANSPLANT',48,36,70,35,7,'SPRING','2025-02-28 20:17:00.750951','2025-02-28 20:17:00.750958',1,31),
 (42,'Sungold Select (cherry)','','','TRANSPLANT',48,36,70,35,7,'SPRING','2025-02-28 20:17:45.554359','2025-02-28 20:17:45.554427',1,31),
 (43,'Rossella  (cherry)','','','TRANSPLANT',48,36,70,35,7,'SPRING','2025-02-28 20:17:34.715000','2025-02-28 20:17:34.715008',1,31),
 (44,'Indigo Cherry Drops (cherry)','','','TRANSPLANT',48,36,70,35,7,'SPRING','2025-02-28 20:17:12.980610','2025-02-28 20:17:12.980617',1,31),
 (45,'Lensmire Purple (cherry)','','','TRANSPLANT',48,36,70,35,7,'SPRING','2025-02-28 20:17:18.807507','2025-02-28 20:17:18.807514',1,31),
 (46,'Lensmire Red (cherry)','','','TRANSPLANT',48,36,70,35,7,'SPRING','2025-02-28 20:17:26.723612','2025-02-28 20:17:26.723621',1,31),
 (47,'Valencia (slicing)','','','TRANSPLANT',48,36,75,35,7,'SPRING','2025-02-28 20:19:25.216070','2025-02-28 20:19:25.216078',1,31),
 (48,'Bush Beefsteak (D) (slicing)','','','TRANSPLANT',48,36,75,35,7,'SPRING','2025-02-28 20:18:06.813808','2025-02-28 20:18:06.813814',1,31),
 (49,'Cambell''s 33 (D) (slicing)','','','TRANSPLANT',48,36,75,35,7,'SPRING','2025-02-28 20:18:32.630913','2025-02-28 20:18:32.630922',1,31),
 (50,'New Yorker (D) (slicing)','','','TRANSPLANT',48,36,75,35,7,'SPRING','2025-02-28 20:18:44.503028','2025-02-28 20:18:44.503036',1,31),
 (51,'Super Sioux (slicing)','','','TRANSPLANT',48,36,75,35,7,'SPRING','2025-02-28 20:18:59.853499','2025-02-28 20:18:59.853506',1,31),
 (52,'Wisconsin 55 (slicing)','','','TRANSPLANT',48,36,75,35,7,'SPRING','2025-02-28 20:19:37.685257','2025-02-28 20:19:37.685264',1,31),
 (53,'Fall Gold','','','TRANSPLANT',36,60,0,0,0,'SPRING','2025-02-27 21:39:20.334274','2025-02-27 21:39:20.334308',1,61),
 (54,'Benary Giant Mix','','','TRANSPLANT',9,12,75,28,7,'SPRING','2025-02-27 21:39:39.413818','2025-02-27 21:39:39.413853',1,48),
 (55,'Queeny Formula Mix','','','TRANSPLANT',9,12,75,28,7,'SPRING','2025-02-27 21:39:52.679438','2025-02-27 21:39:52.679494',1,48),
 (56,'Oklahoma Formula Mix','','','TRANSPLANT',9,12,75,28,7,'SPRING','2025-02-27 21:40:03.971671','2025-02-27 21:40:03.971705',1,48),
 (57,'Lensmire Orange (small)','','','TRANSPLANT',24,24,70,42,7,'SPRING','2025-02-28 20:03:59.668721','2025-02-28 20:03:59.668757',1,19),
 (58,'Lensmire Red (small)','','','TRANSPLANT',24,24,70,42,7,'SPRING','2025-02-28 20:04:12.156820','2025-02-28 20:04:12.156856',1,19),
 (59,'Lensmire Yellow (small)','','','TRANSPLANT',24,24,70,42,7,'SPRING','2025-02-28 20:04:26.033196','2025-02-28 20:04:26.033229',1,19),
 (60,'Red Belgian (small)','','','TRANSPLANT',24,24,70,42,7,'SPRING','2025-02-28 20:04:37.961185','2025-02-28 20:04:37.961242',1,19),
 (61,'Lensmire Orange','','','TRANSPLANT',18,36,NULL,NULL,NULL,'SUMMER','2025-02-28 20:14:35.186771','2025-02-28 20:14:35.186808',1,63),
 (62,'Enterprise (co-op 30) EMLA 7','','','TRANSPLANT',180,240,0,0,0,'SPRING','2025-02-28 21:15:11.507389','2025-02-28 21:15:11.507437',1,65),
 (63,'Liberty EMLA 7','','','TRANSPLANT',180,240,0,0,0,'SPRING','2025-02-28 21:15:36.004459','2025-02-28 21:15:36.004507',1,65),
 (64,'Northern Spy EMLA 7','','','TRANSPLANT',180,240,0,0,0,'SPRING','2025-02-28 21:15:51.342273','2025-02-28 21:15:51.342311',1,65),
 (65,'GoldRush (Co-op 38 Cltv) G-890','','','TRANSPLANT',180,240,0,0,0,'SPRING','2025-02-28 21:16:23.720576','2025-02-28 21:16:23.720609',1,65),
 (66,'Nittany G-890','','','TRANSPLANT',180,240,0,0,0,'SPRING','2025-02-28 21:16:40.091259','2025-02-28 21:16:40.091294',1,65),
 (67,'Crimson Gala (Waliser) G-969','','','TRANSPLANT',180,240,0,0,0,'SPRING','2025-02-28 21:17:00.477725','2025-02-28 21:17:00.477761',1,65),
 (68,'CrimsonCrisp (PP#16622) G-969','','','TRANSPLANT',180,240,0,0,0,'SPRING','2025-02-28 21:17:25.353214','2025-02-28 21:17:25.353250',1,65),
 (69,'Lensmire','','','ROOT_DIVIDING',36,48,NULL,NULL,NULL,'SPRING','2025-02-28 22:17:24.806653','2025-02-28 22:17:24.806662',1,68);
CREATE INDEX IF NOT EXISTS "plants_plant_group_id_3a3d0ab1" ON "plants_plant" (
	"group_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "plants_plant_companion_plants_from_plant_id_to_plant_id_8d2154ec_uniq" ON "plants_plant_companion_plants" (
	"from_plant_id",
	"to_plant_id"
);
CREATE INDEX IF NOT EXISTS "plants_plant_companion_plants_from_plant_id_730b90c0" ON "plants_plant_companion_plants" (
	"from_plant_id"
);
CREATE INDEX IF NOT EXISTS "plants_plant_companion_plants_to_plant_id_da6d98d5" ON "plants_plant_companion_plants" (
	"to_plant_id"
);
CREATE INDEX IF NOT EXISTS "plants_variety_group_id_4c1281e4" ON "plants_variety" (
	"group_id"
);
CREATE INDEX IF NOT EXISTS "plants_variety_variety_plant_id_e398f2bd" ON "plants_variety" (
	"variety_plant_id"
);
CREATE INDEX IF NOT EXISTS "plants_varieties_variety_plant_id_82776288" ON "plants_variety" (
	"variety_plant_id"
);
COMMIT;
